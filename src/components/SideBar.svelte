<script lang="ts">
	import { pageState } from "../libs/pageState";
	import { change_page } from "../libs/pageState";
	import SideButton from "./SideButton.svelte";
	import { chosen_color } from "../libs/preferences";

	let currentPage: number = 1;
	$: currentPage = $pageState;
</script>

<div class="container">
	<div class="active-indicator" style="top: {(currentPage-1) * (80+14)+12}px; background-color: {$chosen_color};"></div>
	<div class="sidebar-buttons">
		<SideButton
			icon={"/icons/home.svg"}
			label="Home"
			active={currentPage === 1}
			onClick={() => change_page(1)}
		/>
		<SideButton
			icon={"/icons/upload.svg"}
			label="Upload"
			active={currentPage === 2}
			onClick={() => change_page(2)}
		/>
		<SideButton
			icon={"/icons/database.svg"}
			label="Database"
			active={currentPage === 3}
			onClick={() => change_page(3)}
		/>
		<SideButton
			icon={"/icons/network.svg"}
			label="Memory"
			active={currentPage === 4}
			onClick={() => change_page(4)}
		/>
		<SideButton
			icon={"/icons/settings.svg"}
			label="Settings"
			active={currentPage === 5}
			onClick={() => change_page(5)}
		/>
	</div>
</div>

<style>
.container {
	position: relative;
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: #161616;
	padding: 10px 0;
}


.active-indicator {
	position: absolute;
	left: 0;
	width: 4px;
	height: 75px;
	border-radius: 2px;
	transition: top 0.3s;
}

.sidebar-buttons {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 14px;
}

.sidebar-buttons {
	margin-bottom: auto;
}
</style>
