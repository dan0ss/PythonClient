<script>
	import {
		createSvelteTable,
		flexRender,
		getCoreRowModel,
		getSortedRowModel,
		getFilteredRowModel,
		getPaginationRowModel
	} from '@tanstack/svelte-table';
	import Sparkles from 'lucide-svelte/icons/sparkles';
	import BadgeCheck from 'lucide-svelte/icons/badge-check';
	import Bot from 'lucide-svelte/icons/bot';
	import Search from 'lucide-svelte/icons/search';
	import ChevronUp from 'lucide-svelte/icons/chevron-up';
	import ChevronDown from 'lucide-svelte/icons/chevron-down';
	import ChevronsUpDown from 'lucide-svelte/icons/chevrons-up-down';
	import ChevronLeft from 'lucide-svelte/icons/chevron-left';
	import ChevronRight from 'lucide-svelte/icons/chevron-right';
	import ChevronsLeft from 'lucide-svelte/icons/chevrons-left';
	import ChevronsRight from 'lucide-svelte/icons/chevrons-right';

	export let data = [];

	let aiFilter = '';
	let organicFilter = '';
	let aiModeFilter = '';
	let aiSorting = [];
	let organicSorting = [];
	let aiModeSorting = [];

	$: aiOverviewData = data.filter(d => d.result_type === 'ai_overview');
	$: organicData = data.filter(d => d.result_type === 'organic');
	$: aiModeData = data.filter(d => d.result_type === 'ai_mode');

	const aiColumns = [
		{ header: 'Keyword', accessorKey: 'keyword', size: 200 },
		{
			header: 'Source',
			accessorKey: 'references_source',
			cell: info => info.getValue() || '-',
			size: 150
		},
		{
			header: 'Domain',
			accessorKey: 'domain',
			cell: info => info.getValue()?.replace(/^www\./, '') || '-',
			size: 180
		},
		{
			header: 'Reference Text',
			accessorKey: 'references_text',
			cell: info => {
				const val = info.getValue();
				return val ? val.slice(0, 80) + (val.length > 80 ? '...' : '') : '-';
			},
			size: 300
		},
		{
			header: 'URL',
			accessorKey: 'references_url',
			cell: info => {
				const val = info.getValue();
				return val ? val.slice(0, 45) + (val.length > 45 ? '...' : '') : '-';
			},
			size: 200
		}
	];

	const organicColumns = [
		{ header: 'Keyword', accessorKey: 'keyword', size: 180 },
		{
			header: 'Rank',
			accessorKey: 'rank_group',
			cell: info => info.getValue() ?? '-',
			size: 60
		},
		{
			header: 'Page',
			accessorKey: 'page',
			cell: info => info.getValue() ?? '-',
			size: 60
		},
		{
			header: 'Domain',
			accessorKey: 'domain',
			cell: info => info.getValue()?.replace(/^www\./, '') || '-',
			size: 160
		},
		{
			header: 'Title',
			accessorKey: 'title',
			cell: info => {
				const val = info.getValue();
				return val ? val.slice(0, 50) + (val.length > 50 ? '...' : '') : '-';
			},
			size: 220
		},
		{
			header: 'Description',
			accessorKey: 'description',
			cell: info => {
				const val = info.getValue();
				return val ? val.slice(0, 60) + (val.length > 60 ? '...' : '') : '-';
			},
			size: 250
		},
		{
			header: 'URL',
			accessorKey: 'url',
			cell: info => {
				const val = info.getValue();
				return val ? val.slice(0, 40) + (val.length > 40 ? '...' : '') : '-';
			},
			size: 180
		}
	];

	$: aiTable = createSvelteTable({
		get data() { return aiOverviewData; },
		columns: aiColumns,
		state: {
			get globalFilter() { return aiFilter; },
			get sorting() { return aiSorting; }
		},
		onSortingChange: (updater) => {
			aiSorting = typeof updater === 'function' ? updater(aiSorting) : updater;
		},
		onGlobalFilterChange: (updater) => {
			aiFilter = typeof updater === 'function' ? updater(aiFilter) : updater;
		},
		getCoreRowModel: getCoreRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel(),
		getPaginationRowModel: getPaginationRowModel()
	});

	$: organicTable = createSvelteTable({
		get data() { return organicData; },
		columns: organicColumns,
		state: {
			get globalFilter() { return organicFilter; },
			get sorting() { return organicSorting; }
		},
		onSortingChange: (updater) => {
			organicSorting = typeof updater === 'function' ? updater(organicSorting) : updater;
		},
		onGlobalFilterChange: (updater) => {
			organicFilter = typeof updater === 'function' ? updater(organicFilter) : updater;
		},
		getCoreRowModel: getCoreRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel(),
		getPaginationRowModel: getPaginationRowModel()
	});

	// AI Mode columns
	const aiModeColumns = [
		{ header: 'Keyword', accessorKey: 'keyword', size: 200 },
		{
			header: 'Summary',
			accessorKey: 'ai_mode_summary',
			cell: info => {
				const val = info.getValue();
				return val ? val.slice(0, 100) + (val.length > 100 ? '...' : '') : '-';
			},
			size: 350
		},
		{
			header: 'Domain',
			accessorKey: 'domain',
			cell: info => info.getValue()?.replace(/^www\./, '') || '-',
			size: 180
		},
		{
			header: 'Citations',
			accessorKey: 'ai_mode_citations_count',
			cell: info => info.getValue() || '-',
			size: 80
		},
		{
			header: 'Primary URL',
			accessorKey: 'ai_mode_primary_url',
			cell: info => {
				const val = info.getValue();
				return val ? val.slice(0, 50) + (val.length > 50 ? '...' : '') : '-';
			},
			size: 220
		}
	];

	$: aiModeTable = createSvelteTable({
		get data() { return aiModeData; },
		columns: aiModeColumns,
		state: {
			get globalFilter() { return aiModeFilter; },
			get sorting() { return aiModeSorting; }
		},
		onSortingChange: (updater) => {
			aiModeSorting = typeof updater === 'function' ? updater(aiModeSorting) : updater;
		},
		onGlobalFilterChange: (updater) => {
			aiModeFilter = typeof updater === 'function' ? updater(aiModeFilter) : updater;
		},
		getCoreRowModel: getCoreRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel(),
		getPaginationRowModel: getPaginationRowModel()
	});

	function openUrl(url) {
		if (url) window.open(url, '_blank');
	}
</script>

<div class="tables-container">
	<!-- AI Overviews Table -->
	<section class="table-section">
		<div class="section-header">
			<div class="header-left">
				<div class="header-icon header-icon--purple">
					<Sparkles size={18} strokeWidth={2} />
				</div>
				<div class="header-text">
					<h2>AI Overviews</h2>
					<span class="record-count">{aiOverviewData.length} references</span>
				</div>
			</div>
			
			<div class="search-box">
				<Search size={16} strokeWidth={2} />
				<input
					type="text"
					placeholder="Search..."
					bind:value={aiFilter}
				/>
			</div>
		</div>

		<div class="table-wrapper">
			<table>
				<thead>
					{#each $aiTable.getHeaderGroups() as headerGroup}
						<tr>
							{#each headerGroup.headers as header}
								<th
									class:sortable={header.column.getCanSort()}
									on:click={header.column.getToggleSortingHandler()}
									style="width: {header.getSize()}px"
								>
									<div class="th-content">
										{#if !header.isPlaceholder}
											<svelte:component
												this={flexRender(header.column.columnDef.header, header.getContext())}
											/>
										{/if}
										
										{#if header.column.getIsSorted() === 'asc'}
											<ChevronUp size={14} strokeWidth={2} class="sort-icon" />
										{:else if header.column.getIsSorted() === 'desc'}
											<ChevronDown size={14} strokeWidth={2} class="sort-icon" />
										{:else if header.column.getCanSort()}
											<ChevronsUpDown size={14} strokeWidth={2} class="sort-icon sort-icon--inactive" />
										{/if}
									</div>
								</th>
							{/each}
						</tr>
					{/each}
				</thead>
				<tbody>
					{#each $aiTable.getRowModel().rows as row}
						<tr on:click={() => openUrl(row.original.references_url)}>
							{#each row.getVisibleCells() as cell}
								<td>
									<svelte:component
										this={flexRender(cell.column.columnDef.cell, cell.getContext())}
									/>
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="table-footer">
			<div class="page-size">
				<span>Rows:</span>
				<select
					value={$aiTable.getState().pagination.pageSize}
					on:change={(e) => $aiTable.setPageSize(Number(e.target.value))}
				>
					{#each [5, 10, 20] as size}
						<option value={size}>{size}</option>
					{/each}
				</select>
			</div>

			<div class="pagination-controls">
				<button on:click={() => $aiTable.setPageIndex(0)} disabled={!$aiTable.getCanPreviousPage()}>
					<ChevronsLeft size={16} strokeWidth={2} />
				</button>
				<button on:click={() => $aiTable.previousPage()} disabled={!$aiTable.getCanPreviousPage()}>
					<ChevronLeft size={16} strokeWidth={2} />
				</button>
				
				<span class="page-indicator">
					{$aiTable.getState().pagination.pageIndex + 1} / {$aiTable.getPageCount() || 1}
				</span>
				
				<button on:click={() => $aiTable.nextPage()} disabled={!$aiTable.getCanNextPage()}>
					<ChevronRight size={16} strokeWidth={2} />
				</button>
				<button on:click={() => $aiTable.setPageIndex($aiTable.getPageCount() - 1)} disabled={!$aiTable.getCanNextPage()}>
					<ChevronsRight size={16} strokeWidth={2} />
				</button>
			</div>
		</div>
	</section>

	<!-- Organic Results Table -->
	<section class="table-section">
		<div class="section-header">
			<div class="header-left">
				<div class="header-icon header-icon--green">
					<BadgeCheck size={18} strokeWidth={2} />
				</div>
				<div class="header-text">
					<h2>Organic Results</h2>
					<span class="record-count">{organicData.length} results</span>
				</div>
			</div>
			
			<div class="search-box">
				<Search size={16} strokeWidth={2} />
				<input
					type="text"
					placeholder="Search..."
					bind:value={organicFilter}
				/>
			</div>
		</div>

		<div class="table-wrapper">
			<table>
				<thead>
					{#each $organicTable.getHeaderGroups() as headerGroup}
						<tr>
							{#each headerGroup.headers as header}
								<th
									class:sortable={header.column.getCanSort()}
									on:click={header.column.getToggleSortingHandler()}
									style="width: {header.getSize()}px"
								>
									<div class="th-content">
										{#if !header.isPlaceholder}
											<svelte:component
												this={flexRender(header.column.columnDef.header, header.getContext())}
											/>
										{/if}
										
										{#if header.column.getIsSorted() === 'asc'}
											<ChevronUp size={14} strokeWidth={2} class="sort-icon" />
										{:else if header.column.getIsSorted() === 'desc'}
											<ChevronDown size={14} strokeWidth={2} class="sort-icon" />
										{:else if header.column.getCanSort()}
											<ChevronsUpDown size={14} strokeWidth={2} class="sort-icon sort-icon--inactive" />
										{/if}
									</div>
								</th>
							{/each}
						</tr>
					{/each}
				</thead>
				<tbody>
					{#each $organicTable.getRowModel().rows as row}
						<tr on:click={() => openUrl(row.original.url)}>
							{#each row.getVisibleCells() as cell}
								<td>
									<svelte:component
										this={flexRender(cell.column.columnDef.cell, cell.getContext())}
									/>
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="table-footer">
			<div class="page-size">
				<span>Rows:</span>
				<select
					value={$organicTable.getState().pagination.pageSize}
					on:change={(e) => $organicTable.setPageSize(Number(e.target.value))}
				>
					{#each [10, 20, 50] as size}
						<option value={size}>{size}</option>
					{/each}
				</select>
			</div>

			<div class="pagination-controls">
				<button on:click={() => $organicTable.setPageIndex(0)} disabled={!$organicTable.getCanPreviousPage()}>
					<ChevronsLeft size={16} strokeWidth={2} />
				</button>
				<button on:click={() => $organicTable.previousPage()} disabled={!$organicTable.getCanPreviousPage()}>
					<ChevronLeft size={16} strokeWidth={2} />
				</button>
				
				<span class="page-indicator">
					{$organicTable.getState().pagination.pageIndex + 1} / {$organicTable.getPageCount() || 1}
				</span>
				
				<button on:click={() => $organicTable.nextPage()} disabled={!$organicTable.getCanNextPage()}>
					<ChevronRight size={16} strokeWidth={2} />
				</button>
				<button on:click={() => $organicTable.setPageIndex($organicTable.getPageCount() - 1)} disabled={!$organicTable.getCanNextPage()}>
					<ChevronsRight size={16} strokeWidth={2} />
				</button>
			</div>
		</div>
	</section>

	<!-- Google AI Mode Table -->
	<section class="table-section">
		<div class="section-header">
			<div class="header-left">
				<div class="header-icon header-icon--cyan">
					<Bot size={18} strokeWidth={2} />
				</div>
				<div class="header-text">
					<h2>Google AI Mode</h2>
					<span class="record-count">{aiModeData.length} results</span>
				</div>
			</div>
			
			<div class="search-box">
				<Search size={16} strokeWidth={2} />
				<input
					type="text"
					placeholder="Search..."
					bind:value={aiModeFilter}
				/>
			</div>
		</div>

		<div class="table-wrapper">
			<table>
				<thead>
					{#each $aiModeTable.getHeaderGroups() as headerGroup}
						<tr>
							{#each headerGroup.headers as header}
								<th
									class:sortable={header.column.getCanSort()}
									on:click={header.column.getToggleSortingHandler()}
									style="width: {header.getSize()}px"
								>
									<div class="th-content">
										{#if !header.isPlaceholder}
											<svelte:component
												this={flexRender(header.column.columnDef.header, header.getContext())}
											/>
										{/if}
										
										{#if header.column.getIsSorted() === 'asc'}
											<ChevronUp size={14} strokeWidth={2} class="sort-icon" />
										{:else if header.column.getIsSorted() === 'desc'}
											<ChevronDown size={14} strokeWidth={2} class="sort-icon" />
										{:else if header.column.getCanSort()}
											<ChevronsUpDown size={14} strokeWidth={2} class="sort-icon sort-icon--inactive" />
										{/if}
									</div>
								</th>
							{/each}
						</tr>
					{/each}
				</thead>
				<tbody>
					{#each $aiModeTable.getRowModel().rows as row}
						<tr on:click={() => openUrl(row.original.ai_mode_primary_url || row.original.references_url)}>
							{#each row.getVisibleCells() as cell}
								<td>
									<svelte:component
										this={flexRender(cell.column.columnDef.cell, cell.getContext())}
									/>
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="table-footer">
			<div class="page-size">
				<span>Rows:</span>
				<select
					value={$aiModeTable.getState().pagination.pageSize}
					on:change={(e) => $aiModeTable.setPageSize(Number(e.target.value))}
				>
					{#each [5, 10, 20] as size}
						<option value={size}>{size}</option>
					{/each}
				</select>
			</div>

			<div class="pagination-controls">
				<button on:click={() => $aiModeTable.setPageIndex(0)} disabled={!$aiModeTable.getCanPreviousPage()}>
					<ChevronsLeft size={16} strokeWidth={2} />
				</button>
				<button on:click={() => $aiModeTable.previousPage()} disabled={!$aiModeTable.getCanPreviousPage()}>
					<ChevronLeft size={16} strokeWidth={2} />
				</button>
				
				<span class="page-indicator">
					{$aiModeTable.getState().pagination.pageIndex + 1} / {$aiModeTable.getPageCount() || 1}
				</span>
				
				<button on:click={() => $aiModeTable.nextPage()} disabled={!$aiModeTable.getCanNextPage()}>
					<ChevronRight size={16} strokeWidth={2} />
				</button>
				<button on:click={() => $aiModeTable.setPageIndex($aiModeTable.getPageCount() - 1)} disabled={!$aiModeTable.getCanNextPage()}>
					<ChevronsRight size={16} strokeWidth={2} />
				</button>
			</div>
		</div>
	</section>
</div>

<style>
	.tables-container {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.table-section {
		background: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-lg);
		overflow: hidden;
		box-shadow: var(--shadow-sm);
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--border-color);
		gap: 1rem;
		flex-wrap: wrap;
	}

	.header-left {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.header-icon {
		width: 36px;
		height: 36px;
		border-radius: var(--radius-md);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.header-icon--purple {
		background: rgba(147, 51, 234, 0.1);
		color: var(--accent-purple);
	}

	.header-icon--green {
		background: rgba(16, 185, 129, 0.1);
		color: var(--accent-green);
	}

	.header-icon--cyan {
		background: rgba(6, 182, 212, 0.1);
		color: #06b6d4;
	}

	.header-text {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.header-text h2 {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.record-count {
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.search-box {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: var(--bg-elevated);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-md);
		padding: 0.5rem 0.75rem;
		transition: border-color 0.2s ease, box-shadow 0.2s ease;
		color: var(--text-muted);
	}

	.search-box:focus-within {
		border-color: var(--accent-blue);
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
	}

	.search-box input {
		background: none;
		border: none;
		color: var(--text-primary);
		font-size: 0.875rem;
		width: 160px;
		outline: none;
	}

	.search-box input::placeholder {
		color: var(--text-muted);
	}

	.table-wrapper {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.8125rem;
	}

	thead {
		background: var(--bg-elevated);
	}

	th {
		text-align: left;
		padding: 0.75rem 1rem;
		font-weight: 600;
		color: var(--text-muted);
		text-transform: uppercase;
		font-size: 0.6875rem;
		letter-spacing: 0.04em;
		white-space: nowrap;
		user-select: none;
	}

	th.sortable {
		cursor: pointer;
	}

	th.sortable:hover {
		color: var(--text-secondary);
		background: var(--bg-primary);
	}

	.th-content {
		display: flex;
		align-items: center;
		gap: 0.375rem;
	}

	.th-content :global(.sort-icon) {
		color: var(--accent-blue);
	}

	.th-content :global(.sort-icon--inactive) {
		opacity: 0.3;
	}

	tbody tr {
		border-bottom: 1px solid var(--border-color);
		transition: background 0.15s ease;
		cursor: pointer;
	}

	tbody tr:hover {
		background: var(--bg-elevated);
	}

	td {
		padding: 0.75rem 1rem;
		color: var(--text-primary);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 300px;
	}

	.table-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1.25rem;
		border-top: 1px solid var(--border-color);
		background: var(--bg-elevated);
	}

	.page-size {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.page-size select {
		padding: 0.375rem 0.5rem;
		background: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-sm);
		color: var(--text-primary);
		font-size: 0.75rem;
		cursor: pointer;
	}

	.pagination-controls {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.pagination-controls button {
		width: 28px;
		height: 28px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-sm);
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.pagination-controls button:hover:not(:disabled) {
		border-color: var(--accent-blue);
		color: var(--accent-blue);
	}

	.pagination-controls button:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	.page-indicator {
		min-width: 50px;
		text-align: center;
		font-size: 0.75rem;
		color: var(--text-muted);
		font-weight: 500;
	}
</style>
