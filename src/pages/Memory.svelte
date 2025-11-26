<script lang="ts">
	import { onMount } from "svelte";
	import { fly } from "svelte/transition";
	import { pyInvoke } from "tauri-plugin-pytauri-api";
	import { type EmotionStatsByYear, type EmotionStats } from "../libs/types";
	import EmotionRegion from "../components/EmotionRegion.svelte";
	import { packCircles } from "../libs/emotions";
	import { windowSize } from "../libs/windowState";
	import { type MessageType } from "../libs/types";
	import Message from "../components/Message.svelte";
	import { chosen_color } from "../libs/preferences";

	let emotionData: EmotionStatsByYear;
	let currentEmotions: EmotionStats;
	let selectedYear: string = "all";
	let availableYears: string[] = [];

	function pack_regions(width: number, height: number) {
		if (currentEmotions?.emotions) {
			currentEmotions.emotions = packCircles(
				currentEmotions.emotions, 
				width - 150, 
				height - 40
			);
		}
	}

	onMount(async () => {
		emotionData = await pyInvoke<EmotionStatsByYear>("get_yearly_emotions");
		availableYears = ["all", ...Object.keys(emotionData.by_year).sort().reverse()];
		currentEmotions = emotionData.all_years;
		pack_regions($windowSize.width, $windowSize.height);
	});

	$: if (emotionData) {
		currentEmotions = selectedYear === "all" 
			? emotionData.all_years 
			: emotionData.by_year[selectedYear];
		pack_regions($windowSize.width, $windowSize.height);
	}

	$: pack_regions($windowSize.width, $windowSize.height);

	let searchQuery: string = "";
	let searchResults: MessageType[] = [];
	let isSearching: boolean = false;
	let searchError: string | null = null;
	let searchTimeout: number;
	let searchEngine: "vector" | "linear" = "vector";

	function debouncedSearch(query: string) {
		clearTimeout(searchTimeout);
		
		if (!query || query.trim().length < 2) {
			searchResults = [];
			isSearching = false;
			return;
		}

		isSearching = true;
		searchTimeout = setTimeout(async () => {
			try {
				const response = await pyInvoke<Array<MessageType>>("search_messages", {
					query: query.trim(), 
					engine: searchEngine
				});
				searchResults = response;
				searchError = null;
			} catch (error) {
				console.error("Search failed:", error);
				searchError = String(error);
				searchResults = [];
			} finally {
				isSearching = false;
			}
		}, 300);
	}

	$: debouncedSearch(searchQuery);
	$: {searchEngine; debouncedSearch(searchQuery);}
</script>

<main class="container" style="--accent: {$chosen_color}">
	<!-- Year Slider -->
	<div class="year-slider">
		<div class="slider-header">Years</div>
		<div class="slider-years">
			{#each availableYears as year}
				<button 
					class="year-button" 
					class:active={selectedYear === year}
					on:click={() => selectedYear = year}
				>
					{year === "all" ? "All" : year}
				</button>
			{/each}
		</div>
		{#if currentEmotions}
			<div class="year-stats">
				<div class="stat-item">
					<div class="stat-label">Messages</div>
					<div class="stat-value">{currentEmotions.total_messages.toLocaleString()}</div>
				</div>
			</div>
		{/if}
	</div>

	<div class="content">
		<div class="search-header">
			<input 
				bind:value={searchQuery} 
				type="text"
				placeholder="Search messages..."
			>
			<select bind:value={searchEngine} class="engine-selector">
				<option value="vector">Vector</option>
				<option value="linear">Linear</option>
			</select>
		</div>
		
		{#if currentEmotions}
			{#key selectedYear}
				<div class="regions" class:dimmed={searchQuery.trim().length > 0}>
					{#each currentEmotions.emotions as emotion}
						<EmotionRegion
							name={emotion.name}
							percent={emotion.percent}
							x={emotion.x}
							y={emotion.y}
							r={emotion.r}
						/>
					{/each}
				</div>
			{/key}
		{:else}
			<p class="loading-text">Loading emotional regions...</p>
		{/if}
	</div>

	{#if searchQuery.trim().length > 0}
		<div class="search-panel" transition:fly={{ x: 300, duration: 300 }}>
			<div class="search-results">
				{#if isSearching}
					<div class="status-message loading">
						<div class="spinner"></div>
						Searching...
					</div>
				{:else if searchError}
					<div class="status-message error">
						<img style="width: 24px; height: 24px; filter: invert(1);" src="error.svg" alt="error">
						{searchError}
					</div>
				{:else if searchResults.length > 0}
					{#each searchResults as message}
						<Message {message} jumpButton={true} showFullDate={true}/>
					{/each}
				{:else}
					<div class="status-message no-results">
						<img style="width: 24px; height: 24px; filter: invert(1);" src="search.svg" alt="search">
						No messages found
					</div>
				{/if}
			</div>
		</div>
	{/if}
</main>

<style>
.container {
	position: relative;
	background-color: #121212;
	width: 100%;
	height: 100%;
	color: #E5E5E5;
	overflow: hidden;
}

.year-slider {
	position: absolute;
	left: 20px;
	top: 50%;
	transform: translateY(-50%);
	width: 70px;
	max-height: calc(100% - 100px);
	background: rgba(22, 22, 22, 0.95);
	backdrop-filter: blur(10px);
	border: 0.1rem solid rgba(255, 255, 255, 0.3);
	border-radius: 16px;
	display: flex;
	flex-direction: column;
	padding: 15px 8px;
	gap: 12px;
	overflow-y: auto;
	z-index: 10;
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.year-slider::-webkit-scrollbar {
	width: 4px;
}

.year-slider::-webkit-scrollbar-track {
	background: transparent;
}

.year-slider::-webkit-scrollbar-thumb {
	background: rgba(255, 255, 255, 0.2);
	border-radius: 2px;
}

.slider-header {
	font-size: 11px;
	font-weight: 700;
	text-transform: uppercase;
	color: rgba(255, 255, 255, 0.5);
	font-weight: 700;
	text-align: center;
	margin-bottom: 8px;
	font-family: 'Nunito', 'monospace';
}

.slider-years {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.year-button {
	background: rgba(255, 255, 255, 0.05);
	border: 1px solid rgba(255, 255, 255, 0.15);
	color: #E5E5E5;
	padding: 10px 6px;
	border-radius: 10px;
	cursor: pointer;
	font-size: 13px;
	font-weight: 700;
	font-family: 'Nunito', monospace;
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	text-align: center;
}

.year-button:hover {
	background: rgba(255, 255, 255, 0.12);
	border-color: rgba(255, 255, 255, 0.3);
	transform: translateX(2px);
}

.year-button.active {
	background: var(--accent);
	border-color: var(--accent);
	color: #000;
	transform: scale(1.05);
}

.year-stats {
	margin-top: auto;
	padding-top: 12px;
	border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.stat-item {
	text-align: center;
}

.stat-label {
	font-size: 9px;
	color: rgba(255, 255, 255, 0.5);
	text-transform: uppercase;
	letter-spacing: 0.8px;
	margin-bottom: 3px;
	font-family: 'Nunito', sans-serif;
}

.stat-value {
	font-size: 13px;
	font-weight: 700;
	color: var(--accent);
	font-family: 'Nunito', monospace;
}

.content {
	width: 100%;
	height: 100%;
	position: relative;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.search-header {
	display: flex;
	flex-direction: row;
	gap: 5px;
	position: absolute;
	top: 20px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 10;
	width: min(400px, calc(100% - 40px));
}

input {
	width: 100%;
	padding: 12px 20px;
	border: 1px solid rgba(255, 255, 255, 0.3);
	background: #1a1a1a;
	color: #f1f1f1;
	border-radius: 10px;
	font-size: 15px;
	transition: all 0.3s;
	box-sizing: border-box;
	font-family: 'Nunito', monospace;
	font-weight: 600;
}

.engine-selector {
	padding: 12px 5px;
	border: 1px solid rgba(255, 255, 255, 0.3);
	background: #1a1a1a;
	color: #f1f1f1;
	border-radius: 10px;
	font-size: 15px;
	transition: all 0.3s;
	box-sizing: border-box;
	font-family: 'Nunito', monospace;
	font-weight: 600;
	cursor: pointer;
}

.engine-selector:focus {
	border: 1px solid var(--accent);
	outline: none;
}

input::placeholder {
	color: #fffafaa1;
}

input:focus {
	outline: none;
	background: rgb(8, 8, 8);
	border: 0.1rem solid var(--accent);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.regions {
	width: 100%;
	height: 100%;
	transition: opacity 0.3s, filter 0.3s;
}

.regions.dimmed {
	opacity: 0.4;
	filter: blur(2px);
}

.regions > :global(*) {
	transform: translate(-50%, -50%);
	opacity: 0;
	animation: fadeInScale 0.6s ease-out forwards;
}

@keyframes fadeInScale {
	from {
		opacity: 0;
		transform: translate(-50%, -50%) scale(0.3);
	}
	to {
		opacity: 1;
		transform: translate(-50%, -50%) scale(1);
	}
}

.loading-text {
	color: rgba(229, 229, 229, 0.6);
}

.search-panel {
	position: absolute;
	right: 0;
	top: 0;
	bottom: 0;
	width: 400px;
	background: #161616;
	backdrop-filter: blur(10px);
	overflow: hidden;
	display: flex;
	flex-direction: column;
	font-family: 'Nunito', monospace;
	font-weight: 600;
}

.search-results {
	display: flex;
	flex-direction: column;
	gap: 15px;
	flex: 1;
	overflow-y: auto;
	padding: 80px 20px 20px;
}

.search-results::-webkit-scrollbar {
	width: 8px;
}

.search-results::-webkit-scrollbar-track {
	background: rgba(255, 255, 255, 0.05);
}

.search-results::-webkit-scrollbar-thumb {
	background: rgba(255, 255, 255, 0.2);
	border-radius: 4px;
}

.search-results::-webkit-scrollbar-thumb:hover {
	background: rgba(255, 255, 255, 0.3);
}

.status-message {
	text-align: center;
	padding: 60px 20px;
	color: #888;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 12px;
}

.status-message.error {
	color: #ff6b6b;
}

.spinner {
	width: 24px;
	height: 24px;
	border: 3px solid rgba(255, 255, 255, 0.1);
	border-top-color: #E5E5E5;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

@media (max-width: 768px) {
	.year-slider {
		left: 10px;
		width: 60px;
		padding: 12px 6px;
		max-height: calc(100% - 80px);
	}
	
	.year-button {
		font-size: 11px;
		padding: 8px 4px;
	}
	
	.slider-header {
		font-size: 10px;
	}
	
	.stat-value {
		font-size: 11px;
	}
	
	.search-panel {
		width: 100%;
	}
	
	.regions.dimmed {
		display: none;
	}
}
</style>