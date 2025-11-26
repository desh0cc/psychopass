<script lang="ts">
  export let icon: string;
  export let label: string = "";
  export let active: boolean = false;
  export let onClick: () => void;
</script>

<button class="sidebar-btn {active ? 'active' : ''}" onclick={onClick}>
  <div class="icon-wrapper">
    <img src={icon} alt={label} class="icon" />
  </div>
  <span class="label">{label}</span>
</button>

<style>
  .sidebar-btn {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    border: none;
    border-radius: 12px;
    background: rgb(15, 15, 15);
    cursor: pointer;
    color: #ccc;
    overflow: hidden;
    user-select: none;
    transition: background 0.3s, color 0.3s, box-shadow 0.3s;
  }

  .sidebar-btn:hover {
    color: white;
    border: 1px solid rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.08);
  }

  .sidebar-btn.active {
    color: #fff;
    border: 1px solid rgba(255,255,255,0.3);
    background: linear-gradient(145deg, rgba(255,255,255,0.25), rgba(255,255,255,0.05));
  }

  .icon-wrapper {
    transition: transform 0.3s cubic-bezier(0.23, 1, 0.32, 1);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar-btn.active .icon-wrapper,
  .sidebar-btn:hover .icon-wrapper {
    transform: translateY(-8px) scale(1.1);
  }

  img {
    filter: invert(100%);
    width: 28px;
    height: 28px;
  }

  .label {
    position: absolute;
    bottom: 6px;
    opacity: 0;
    font-family: 'Nunito', monospace;
    font-weight: 700;
    font-size: 0.8rem;
    transform: translateY(12px);
    transition: opacity 0.4s cubic-bezier(0.23, 1, 0.32, 1),
                transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    white-space: nowrap;
    pointer-events: none;
  }

  .sidebar-btn.active .label,
  .sidebar-btn:hover .label {
    opacity: 1;
    transform: translateY(0);
  }
</style>
