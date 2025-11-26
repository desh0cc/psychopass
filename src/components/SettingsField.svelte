<script lang="ts">
	export let label: string = "";
</script>

<div class="settings-field">
	<p class="label">{label}</p>
	<div class="field">
		<slot></slot>
	</div>
</div>

<style>
.settings-field {
	background-color: rgb(26, 25, 25);
	display: flex;
	width: 90%;
	padding-left: 20px;
	padding-right: 20px;
	border-radius: 10px;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
}

.label {
	font-weight: bold;
	font-size: 17px;
}

.field {
	display: flex;
}
</style>
