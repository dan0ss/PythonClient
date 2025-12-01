<script>
	import { onMount, afterUpdate } from 'svelte';
	import { Chart, registerables } from 'chart.js';
	import BarChart3 from 'lucide-svelte/icons/bar-chart-3';

	export let data = [];

	let domainChart;
	let typeChart;
	let rankChart;
	let domainChartInstance;
	let typeChartInstance;
	let rankChartInstance;

	// Enterprise color palette matching design system
	const chartColors = {
		blue: { bg: 'rgba(37, 99, 235, 0.1)', border: '#2563eb' },
		purple: { bg: 'rgba(147, 51, 234, 0.1)', border: '#9333ea' },
		orange: { bg: 'rgba(249, 115, 22, 0.1)', border: '#f97316' },
		green: { bg: 'rgba(16, 185, 129, 0.1)', border: '#10b981' },
		cyan: { bg: 'rgba(6, 182, 212, 0.1)', border: '#06b6d4' }
	};

	const barColors = [
		chartColors.blue.border,
		chartColors.purple.border,
		chartColors.orange.border,
		chartColors.green.border,
		chartColors.blue.border,
		chartColors.purple.border,
		chartColors.orange.border,
		chartColors.green.border
	];

	const chartOptions = {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
			legend: {
				labels: {
					font: { family: 'system-ui, sans-serif', size: 12 },
					color: '#6b7280'
				}
			},
			tooltip: {
				backgroundColor: '#ffffff',
				titleColor: '#111827',
				bodyColor: '#374151',
				borderColor: '#e5e7eb',
				borderWidth: 1,
				padding: 12,
				cornerRadius: 6,
				boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
			}
		},
		scales: {
			x: {
				grid: { color: '#f3f4f6' },
				ticks: { color: '#6b7280', font: { size: 11 } }
			},
			y: {
				grid: { color: '#f3f4f6' },
				ticks: { color: '#6b7280', font: { size: 11 } }
			}
		}
	};

	onMount(() => {
		Chart.register(...registerables);
		Chart.defaults.color = '#6b7280';
		Chart.defaults.borderColor = '#e5e7eb';
		Chart.defaults.font.family = 'system-ui, sans-serif';
		
		createCharts();
	});

	afterUpdate(() => {
		updateCharts();
	});

	function getTopDomains() {
		const domainCounts = {};
		data.forEach(d => {
			if (d.domain) {
				domainCounts[d.domain] = (domainCounts[d.domain] || 0) + 1;
			}
		});
		return Object.entries(domainCounts)
			.sort((a, b) => b[1] - a[1])
			.slice(0, 8);
	}

	function getResultTypes() {
		const types = {};
		data.forEach(d => {
			const type = d.result_type || 'unknown';
			types[type] = (types[type] || 0) + 1;
		});
		return Object.entries(types);
	}

	function getRankDistribution() {
		const organic = data.filter(d => d.result_type === 'organic' && d.rank_group);
		const ranges = {
			'1-3': 0,
			'4-6': 0,
			'7-10': 0,
			'11-15': 0,
			'15+': 0
		};
		organic.forEach(d => {
			const rank = d.rank_group;
			if (rank <= 3) ranges['1-3']++;
			else if (rank <= 6) ranges['4-6']++;
			else if (rank <= 10) ranges['7-10']++;
			else if (rank <= 15) ranges['11-15']++;
			else ranges['15+']++;
		});
		return Object.entries(ranges);
	}

	function createCharts() {
		const topDomains = getTopDomains();
		const resultTypes = getResultTypes();
		const rankDist = getRankDistribution();

		// Domain distribution chart
		if (domainChart) {
			domainChartInstance = new Chart(domainChart, {
				type: 'bar',
				data: {
					labels: topDomains.map(d => d[0].replace(/^www\./, '').slice(0, 20)),
					datasets: [{
						label: 'Results',
						data: topDomains.map(d => d[1]),
						backgroundColor: barColors,
						borderRadius: 4,
						borderSkipped: false
					}]
				},
				options: {
					...chartOptions,
					indexAxis: 'y',
					plugins: {
						...chartOptions.plugins,
						legend: { display: false }
					},
					scales: {
						x: {
							grid: { color: '#f3f4f6' },
							ticks: { color: '#6b7280', font: { size: 11 } }
						},
						y: {
							grid: { display: false },
							ticks: { color: '#6b7280', font: { size: 11 } }
						}
					}
				}
			});
		}

		// Result types chart
		if (typeChart) {
			typeChartInstance = new Chart(typeChart, {
				type: 'doughnut',
				data: {
					labels: resultTypes.map(t => t[0].replace(/_/g, ' ').toUpperCase()),
					datasets: [{
						data: resultTypes.map(t => t[1]),
						backgroundColor: [
							chartColors.blue.border,
							chartColors.purple.border,
							chartColors.green.border,
							chartColors.cyan.border,
							chartColors.orange.border
						],
						borderWidth: 0,
						spacing: 3
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					cutout: '65%',
					plugins: {
						legend: {
							position: 'bottom',
							labels: {
								padding: 16,
								usePointStyle: true,
								pointStyle: 'circle',
								font: { size: 11, family: 'system-ui, sans-serif' },
								color: '#6b7280'
							}
						},
						tooltip: chartOptions.plugins.tooltip
					}
				}
			});
		}

		// Rank distribution chart
		if (rankChart) {
			rankChartInstance = new Chart(rankChart, {
				type: 'bar',
				data: {
					labels: rankDist.map(r => r[0]),
					datasets: [{
						label: 'Results',
						data: rankDist.map(r => r[1]),
						backgroundColor: [
							chartColors.green.border,
							chartColors.blue.border,
							chartColors.purple.border,
							chartColors.orange.border,
							'#6b7280'
						],
						borderRadius: 4,
						borderSkipped: false
					}]
				},
				options: {
					...chartOptions,
					plugins: {
						...chartOptions.plugins,
						legend: { display: false }
					},
					scales: {
						x: {
							grid: { display: false },
							ticks: { color: '#6b7280', font: { size: 11 } }
						},
						y: {
							grid: { color: '#f3f4f6' },
							ticks: { color: '#6b7280', font: { size: 11 } }
						}
					}
				}
			});
		}
	}

	function updateCharts() {
		const topDomains = getTopDomains();
		const resultTypes = getResultTypes();
		const rankDist = getRankDistribution();

		if (domainChartInstance) {
			domainChartInstance.data.labels = topDomains.map(d => d[0].replace(/^www\./, '').slice(0, 20));
			domainChartInstance.data.datasets[0].data = topDomains.map(d => d[1]);
			domainChartInstance.update();
		}

		if (typeChartInstance) {
			typeChartInstance.data.labels = resultTypes.map(t => t[0].replace(/_/g, ' ').toUpperCase());
			typeChartInstance.data.datasets[0].data = resultTypes.map(t => t[1]);
			typeChartInstance.update();
		}

		if (rankChartInstance) {
			rankChartInstance.data.labels = rankDist.map(r => r[0]);
			rankChartInstance.data.datasets[0].data = rankDist.map(r => r[1]);
			rankChartInstance.update();
		}
	}
</script>

<section class="charts-section">
	<div class="section-header">
		<BarChart3 size={18} strokeWidth={2} />
		<h2>Analytics</h2>
	</div>

	<div class="charts-grid">
		<div class="chart-card">
			<div class="chart-header">
				<h3>Top Domains</h3>
				<span class="chart-badge">Distribution</span>
			</div>
			<div class="chart-container chart-container--bar">
				<canvas bind:this={domainChart}></canvas>
			</div>
		</div>

		<div class="chart-card chart-card--small">
			<div class="chart-header">
				<h3>Result Types</h3>
				<span class="chart-badge">Breakdown</span>
			</div>
			<div class="chart-container chart-container--doughnut">
				<canvas bind:this={typeChart}></canvas>
			</div>
		</div>

		<div class="chart-card chart-card--small">
			<div class="chart-header">
				<h3>Rank Distribution</h3>
				<span class="chart-badge chart-badge--green">Organic</span>
			</div>
			<div class="chart-container">
				<canvas bind:this={rankChart}></canvas>
			</div>
		</div>
	</div>
</section>

<style>
	.charts-section {
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

	.charts-grid {
		display: grid;
		grid-template-columns: 1.5fr 1fr 1fr;
		gap: 1rem;
	}

	@media (max-width: 1200px) {
		.charts-grid {
			grid-template-columns: 1fr 1fr;
		}
		
		.chart-card:first-child {
			grid-column: span 2;
		}
	}

	@media (max-width: 768px) {
		.charts-grid {
			grid-template-columns: 1fr;
		}
		
		.chart-card:first-child {
			grid-column: span 1;
		}
	}

	.chart-card {
		background: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-lg);
		padding: 1.25rem;
		box-shadow: var(--shadow-sm);
		transition: box-shadow 0.2s ease;
	}

	.chart-card:hover {
		box-shadow: var(--shadow);
	}

	.chart-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
		padding-bottom: 0.75rem;
		border-bottom: 1px solid var(--border-color);
	}

	.chart-header h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.chart-badge {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--accent-blue);
		background: rgba(37, 99, 235, 0.1);
		padding: 0.25rem 0.5rem;
		border-radius: var(--radius-sm);
		font-weight: 600;
	}

	.chart-badge--green {
		color: var(--accent-green);
		background: rgba(16, 185, 129, 0.1);
	}

	.chart-container {
		height: 250px;
		position: relative;
	}

	.chart-container--bar {
		height: 280px;
	}

	.chart-container--doughnut {
		height: 260px;
	}
</style>
