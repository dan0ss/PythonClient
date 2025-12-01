<script>
	import { onMount } from 'svelte';
	import BarChart3 from 'lucide-svelte/icons/bar-chart-3';
	import FileText from 'lucide-svelte/icons/file-text';
	import AlertCircle from 'lucide-svelte/icons/alert-circle';
	import FolderOpen from 'lucide-svelte/icons/folder-open';
	import Loader2 from 'lucide-svelte/icons/loader-2';
	import SummaryCards from '$lib/components/SummaryCards.svelte';
	import Charts from '$lib/components/Charts.svelte';
	import DataTable from '$lib/components/DataTable.svelte';

	let files = [];
	let selectedFile = '';
	let data = [];
	let loading = false;
	let error = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/files');
			files = await response.json();
			if (files.length > 0 && !files.error) {
				selectedFile = files[0];
				await loadData();
			}
		} catch (e) {
			error = 'Failed to load file list';
		}
	});

	async function loadData() {
		if (!selectedFile) return;
		loading = true;
		error = null;
		try {
			const response = await fetch(`/api/files?file=${encodeURIComponent(selectedFile)}`);
			const result = await response.json();
			if (result.error) {
				error = result.error;
				data = [];
			} else {
				data = result;
			}
		} catch (e) {
			error = 'Failed to load file data';
			data = [];
		}
		loading = false;
	}

	function handleFileChange(event) {
		selectedFile = event.target.value;
		loadData();
	}

	function formatFileName(filename) {
		const match = filename.match(/(\d{8})-(\d{6})/);
		if (match) {
			const date = match[1];
			const time = match[2];
			return `${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)} ${time.slice(0, 2)}:${time.slice(2, 4)}`;
		}
		return filename;
	}
</script>

<svelte:head>
	<title>SERP Analytics Dashboard</title>
</svelte:head>

<div class="dashboard">
	<header class="header">
		<div class="header-content">
			<div class="logo">
				<div class="logo-icon">
					<BarChart3 size={20} strokeWidth={2} />
				</div>
				<div class="logo-text">
					<h1>SERP Analytics</h1>
					<span class="subtitle">Search Results Dashboard</span>
				</div>
			</div>
			
			<div class="file-selector">
				<label for="file-select">
					<FileText size={16} strokeWidth={2} />
					<span>Data Source</span>
				</label>
				<select id="file-select" bind:value={selectedFile} on:change={handleFileChange}>
					{#each files as file}
						<option value={file}>{formatFileName(file)}</option>
					{/each}
				</select>
			</div>
		</div>
	</header>

	<main class="main">
		{#if loading}
			<div class="state-container">
				<div class="spinner">
					<Loader2 size={32} strokeWidth={2} class="animate-spin" />
				</div>
				<span>Loading data...</span>
			</div>
		{:else if error}
			<div class="state-container state-container--error">
				<AlertCircle size={40} strokeWidth={1.5} />
				<span>{error}</span>
			</div>
		{:else if files.length === 0}
			<div class="state-container state-container--empty">
				<FolderOpen size={48} strokeWidth={1.5} />
				<h2>No Data Files Found</h2>
				<p>Add JSON files to the <code>outputs/json</code> directory to get started.</p>
			</div>
		{:else if data.length > 0}
			<SummaryCards {data} />
			<Charts {data} />
			<DataTable {data} />
		{/if}
	</main>

	<footer class="footer">
		<span>DataForSEO SERP & AI Mode Results</span>
		<span class="separator">•</span>
		<span>{data.length} records loaded</span>
	</footer>
</div>

<style>
	.dashboard {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.header {
		background: var(--bg-secondary);
		border-bottom: 1px solid var(--border-color);
		padding: 0.875rem 1.5rem;
		position: sticky;
		top: 0;
		z-index: 100;
	}

	.header-content {
		max-width: 1600px;
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1.5rem;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.logo-icon {
		width: 40px;
		height: 40px;
		background: var(--accent-blue);
		border-radius: var(--radius-md);
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
	}

	.logo-text h1 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.subtitle {
		font-size: 0.6875rem;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.file-selector {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.file-selector label {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		color: var(--text-muted);
		font-size: 0.8125rem;
	}

	.file-selector select {
		padding: 0.5rem 2rem 0.5rem 0.75rem;
		background: var(--bg-elevated);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-md);
		color: var(--text-primary);
		font-size: 0.8125rem;
		font-weight: 500;
		cursor: pointer;
		appearance: none;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 0.5rem center;
		transition: border-color 0.15s ease, box-shadow 0.15s ease;
	}

	.file-selector select:hover {
		border-color: var(--text-muted);
	}

	.file-selector select:focus {
		outline: none;
		border-color: var(--accent-blue);
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
	}

	.main {
		flex: 1;
		padding: 1.5rem;
		max-width: 1600px;
		width: 100%;
		margin: 0 auto;
	}

	.state-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
		gap: 0.75rem;
		color: var(--text-muted);
	}

	.spinner :global(.animate-spin) {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.state-container--error {
		color: var(--accent-orange);
	}

	.state-container--empty {
		color: var(--text-muted);
	}

	.state-container--empty h2 {
		color: var(--text-primary);
		font-size: 1.125rem;
		margin-top: 0.5rem;
	}

	.state-container--empty code {
		font-family: ui-monospace, monospace;
		font-size: 0.8125rem;
		font-weight: 500;
		background: var(--bg-elevated);
		padding: 0.25rem 0.5rem;
		border-radius: var(--radius-sm);
		color: var(--accent-blue);
	}

	.footer {
		padding: 0.75rem 1.5rem;
		text-align: center;
		color: var(--text-muted);
		font-size: 0.75rem;
		border-top: 1px solid var(--border-color);
		background: var(--bg-secondary);
	}

	.separator {
		margin: 0 0.5rem;
		opacity: 0.5;
	}
</style>
