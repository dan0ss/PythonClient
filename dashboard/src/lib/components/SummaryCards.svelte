<script>
	import ClipboardList from 'lucide-svelte/icons/clipboard-list';
	import Hash from 'lucide-svelte/icons/hash';
	import Globe from 'lucide-svelte/icons/globe';
	import Sparkles from 'lucide-svelte/icons/sparkles';
	import BadgeCheck from 'lucide-svelte/icons/badge-check';
	import TrendingUp from 'lucide-svelte/icons/trending-up';
	import LayoutGrid from 'lucide-svelte/icons/layout-grid';
	import Bot from 'lucide-svelte/icons/bot';

	export let data = [];

	$: totalResults = data.length;
	$: uniqueKeywords = [...new Set(data.map(d => d.keyword))].length;
	$: uniqueDomains = [...new Set(data.map(d => d.domain))].length;
	$: aiOverviews = data.filter(d => d.result_type === 'ai_overview').length;
	$: organicResults = data.filter(d => d.result_type === 'organic').length;
	$: aiModeResults = data.filter(d => d.result_type === 'ai_mode').length;
	$: avgRank = organicResults > 0 
		? (data.filter(d => d.rank_group).reduce((sum, d) => sum + d.rank_group, 0) / data.filter(d => d.rank_group).length).toFixed(1)
		: 'N/A';

	const cards = [
		{ label: 'Total Records', icon: ClipboardList, color: 'blue' },
		{ label: 'Keywords', icon: Hash, color: 'purple' },
		{ label: 'Domains', icon: Globe, color: 'blue' },
		{ label: 'AI Overviews', icon: Sparkles, color: 'purple' },
		{ label: 'Organic Results', icon: BadgeCheck, color: 'green' },
		{ label: 'AI Mode', icon: Bot, color: 'cyan' },
		{ label: 'Avg. Rank', icon: TrendingUp, color: 'orange' }
	];

	$: values = [totalResults, uniqueKeywords, uniqueDomains, aiOverviews, organicResults, aiModeResults, avgRank];
</script>

<section class="cards-section">
	<div class="section-header">
		<LayoutGrid size={18} strokeWidth={2} />
		<h2>Overview</h2>
	</div>
	
	<div class="cards-grid">
		{#each cards as card, i}
			<div class="card card--{card.color}">
				<div class="card-icon">
					<svelte:component this={card.icon} size={22} strokeWidth={1.5} />
				</div>
				<div class="card-content">
					<span class="card-label">{card.label}</span>
					<span class="card-value">{values[i]}</span>
				</div>
			</div>
		{/each}
	</div>
</section>

<style>
	.cards-section {
		margin-bottom: 1.5rem;
	}

	.section-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 1rem;
		color: var(--text-muted);
	}

	.section-header h2 {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.cards-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 1rem;
	}

	.card {
		background: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-lg);
		padding: 1.25rem;
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		box-shadow: var(--shadow-sm);
		transition: box-shadow 0.2s ease, transform 0.2s ease;
	}

	.card:hover {
		box-shadow: var(--shadow);
		transform: translateY(-1px);
	}

	.card-icon {
		width: 44px;
		height: 44px;
		border-radius: var(--radius-md);
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.card--blue .card-icon { 
		background: rgba(37, 99, 235, 0.1); 
		color: var(--accent-blue);
	}
	.card--purple .card-icon { 
		background: rgba(147, 51, 234, 0.1); 
		color: var(--accent-purple);
	}
	.card--green .card-icon { 
		background: rgba(16, 185, 129, 0.1); 
		color: var(--accent-green);
	}
	.card--orange .card-icon { 
		background: rgba(249, 115, 22, 0.1); 
		color: var(--accent-orange);
	}
	.card--cyan .card-icon { 
		background: rgba(6, 182, 212, 0.1); 
		color: #06b6d4;
	}

	.card-content {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.card-label {
		font-size: 0.75rem;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.02em;
		font-weight: 500;
	}

	.card-value {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--text-primary);
		line-height: 1;
	}
</style>
