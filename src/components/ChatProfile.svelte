<script lang="ts">
	import { onMount } from "svelte";
	import { type Profile } from "../libs/types";
	import { convertFileSrc } from "@tauri-apps/api/core";
	import { pushOverlay } from "../libs/overlayState";
	import { chosen_color } from "../libs/preferences";

	export let id: string;
	export let name: string;
	export let avatar: string | null;
	export let type: string;
	export let participants: Array<Profile>;

	let members_num: number;

	onMount(() => {
		members_num = participants.length;
	});

	$: participants = participants.map(member => ({
		...member,
		avatar: member.avatar ? convertFileSrc(member.avatar) : "pfp.svg"
	}));

	function openChat() {
		pushOverlay({
			type: 'chat',
			data: { "chat_id": id }
		});
	}

</script>

<button class="container" onclick={openChat} style="--accent: {$chosen_color}">
	<div class="info-div">
			<div class="avatar">
				{#if avatar}
					<img src={convertFileSrc(avatar)} alt={name}>
				{:else if name}
					<div class="placeholder">{(name?.[0] ?? "?").toUpperCase()}</div>
				{:else}
					<div class="placeholder">?</div>
				{/if}
			</div>
		<div class="chat-info">
			<p class="name">{name}</p>
			<p class="type"><span style="font-weight: 700; margin-right:5px;">type:</span>{type}</p>
		</div>
	</div>

	<div class="members-div">
		<div class="members">
			{#each participants.slice(0, 4) as member}
				<div class="member">
					<div class="member-pfp">
						<img src={member.avatar} alt={member.global_name}>
					</div>
					<span class="tooltip-text">
						{member.global_name}
					</span>
				</div>
			{/each}
			{#if participants.length > 5}
				<div class="member-pfp extra">
					+{participants.length - 5}
				</div>
			{/if}
		</div>
	</div>
</button>

<style>
.container {
	display: flex;
	flex-direction: column;
	width: 430px;
	min-height: 200px;
	border-radius: 20px;
	background-color: #222;
	padding: 20px;
	box-shadow: 0 6px 15px rgba(0,0,0,0.4);
	transition: transform 0.2s, box-shadow 0.2s;
	cursor: pointer;
	overflow: auto;
	border: none;
	font-family: 'Nunito', 'monospace';
}

.container:hover {
	transform: translateY(-4px);
	box-shadow: 0 12px 20px rgba(0,0,0,0.5);
}

.info-div {
	display: flex;
	flex-direction: row;
	gap: 15px;
	align-items: center;
}

.avatar {
	flex-shrink: 0;
	width: 75px;
	height: 75px;
	border-radius: 50%;
	overflow: hidden;
	background: #333;
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: bold;
	color: white;
	text-transform: uppercase;
	font-size: 20px;
}

.avatar img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.chat-info {
	display: flex;
	flex-direction: column;
	gap: 2px;
}

.chat-info p {
	text-align: start;
	margin: 2px 0;
}

.chat-info .name {
	font-size: 1.2rem;
	font-weight: 700;
	color: #fff;
}

.chat-info .type {
	font-size: 0.9rem;
	color: #ccc;
}

.members-div {
	margin-top: 15px;
}

.members {
	display: flex;
	flex-direction: row;
	gap: 8px;
	align-items: center;
}

.member-pfp {
	position: relative;
	width: 50px;
	height: 50px;
	border-radius: 50%;
	overflow: hidden;
	transition: transform 0.2s, border-color 0.2s;
}

.member-pfp:hover {
	transform: scale(1.1);
}

.member-pfp img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.member-pfp.extra {
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: #555;
	color: #fff;
	font-weight: 700;
	font-size: 0.9rem;
	border-radius: 50%;
	border: 2px solid #555;
}

.member-pfp {
	position: relative;
	width: 65px;
	height: 65px;
	border-radius: 50%;
	overflow: hidden;
	border: 2px solid #555;
}

.member {
	position: relative;
	display: inline-block;
}

.member .tooltip-text {
	visibility: hidden;
	opacity: 0;
	width: max-content;
	max-width: 200px;
	background-color: #111111;
	color: #fff;
	text-align: center;
	border-radius: 8px;
	padding: 6px 10px;
	position: absolute;
	z-index: 1;
	bottom: 125%;
	left: 50%;
	transform: translateX(-50%);
	transition: opacity 0.25s ease;
	box-shadow: 0 2px 8px rgba(0,0,0,0.2);
	font-family: 'Nunito', 'monospace';
	font-weight: 700;
	font-size: 13px;
	pointer-events: none;
}

.member .tooltip-text::after {
	content: "";
	position: absolute;
	top: 100%;
	left: 50%;
	margin-left: -6px;
	border-width: 6px;
	border-style: solid;
	border-color: #111111 transparent transparent transparent;
}

.member:hover .tooltip-text {
	visibility: visible;
	opacity: 1;
}

</style>
