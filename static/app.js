// Configuration
const REFRESH_INTERVAL = 5000; // 5 secondes
let refreshTimer;

// Éléments du DOM
const elements = {
    // Stats
    totalPortfolio: document.getElementById('total-portfolio'),
    portfolioChange: document.getElementById('portfolio-change'),
    roi: document.getElementById('roi'),
    balance: document.getElementById('balance'),
    totalTrades: document.getElementById('total-trades'),
    winRate: document.getElementById('win-rate'),
    totalPnl: document.getElementById('total-pnl'),

    // Positions
    openCount: document.getElementById('open-count'),
    openPositionsBody: document.getElementById('open-positions-body'),
    historyBody: document.getElementById('history-body'),

    // Bot controls
    btnStart: document.getElementById('btn-start'),
    btnStop: document.getElementById('btn-stop'),
    botStatus: document.getElementById('bot-status'),
    botStatusText: document.getElementById('bot-status-text'),

    // Config
    configSymbols: document.getElementById('config-symbols'),
    configTimeframe: document.getElementById('config-timeframe'),
    configInterval: document.getElementById('config-interval'),
    configScore: document.getElementById('config-score'),
    configRR: document.getElementById('config-rr'),
    configPTEnabled: document.getElementById('config-pt-enabled'),
    configPTBalance: document.getElementById('config-pt-balance'),
    configPTSize: document.getElementById('config-pt-size'),
    configPTMax: document.getElementById('config-pt-max'),
    configPTLeverage: document.getElementById('config-pt-leverage'),
    configPTTrailingStop: document.getElementById('config-pt-trailing-stop'),
    configPTFixedTP: document.getElementById('config-pt-fixed-tp'),
    configPTTrailingTP: document.getElementById('config-pt-trailing-tp'),
    configHoursEnabled: document.getElementById('config-hours-enabled'),
    configHoursRange: document.getElementById('config-hours-range'),
    configHoursDays: document.getElementById('config-hours-days'),

    // Logs
    logsContainer: document.getElementById('logs-container'),

    // Footer
    lastUpdate: document.getElementById('last-update')
};

// Formatage des nombres
function formatCurrency(value) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

function formatPercent(value) {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
}

function formatNumber(value, decimals = 4) {
    return parseFloat(value).toFixed(decimals);
}

// Calcul de la durée
function calculateDuration(startISO) {
    const start = new Date(startISO);
    const now = new Date();
    const diffMs = now - start;
    const diffHours = diffMs / (1000 * 60 * 60);

    if (diffHours < 1) {
        return `${Math.floor(diffHours * 60)}min`;
    } else if (diffHours < 24) {
        return `${diffHours.toFixed(1)}h`;
    } else {
        return `${(diffHours / 24).toFixed(1)}j`;
    }
}

// Mise à jour des statistiques
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        // Portfolio
        const portfolioValue = stats.total_portfolio_value || stats.current_balance || 0;
        elements.totalPortfolio.textContent = formatCurrency(portfolioValue);

        // ROI
        const roi = stats.roi || 0;
        elements.roi.textContent = formatPercent(roi);
        elements.roi.className = `stat-value ${roi >= 0 ? 'pnl-positive' : 'pnl-negative'}`;

        // Portfolio change
        elements.portfolioChange.textContent = formatPercent(roi);
        elements.portfolioChange.className = `stat-change ${roi >= 0 ? 'positive' : 'negative'}`;

        // Balance
        elements.balance.textContent = formatCurrency(stats.current_balance || 0);

        // Trades
        elements.totalTrades.textContent = stats.total_trades || 0;

        // Win rate
        elements.winRate.textContent = `${(stats.win_rate || 0).toFixed(1)}%`;

        // Total P&L
        const totalPnl = stats.total_pnl || 0;
        elements.totalPnl.textContent = formatCurrency(totalPnl);
        elements.totalPnl.className = `stat-value ${totalPnl >= 0 ? 'pnl-positive' : 'pnl-negative'}`;

    } catch (error) {
        console.error('Erreur lors de la mise à jour des stats:', error);
    }
}

// Mise à jour des positions
async function updatePositions() {
    try {
        const response = await fetch('/api/positions');
        const data = await response.json();

        // Positions ouvertes
        const openPositions = data.open || [];
        elements.openCount.textContent = openPositions.length;

        if (openPositions.length === 0) {
            elements.openPositionsBody.innerHTML = '<tr><td colspan="12" class="no-data">Aucune position ouverte</td></tr>';
        } else {
            elements.openPositionsBody.innerHTML = openPositions.map(pos => {
                const pnl = pos.pnl_usdt || 0;
                const pnlPercent = pos.pnl_percent_on_margin || pos.pnl_percent || 0;
                const leverage = pos.leverage || 1;
                
                // Générer l'URL Bitget pour cette paire (nettoyer le symbole en enlevant les /)
                const cleanSymbol = pos.symbol.replace('/', '');
                const bitgetUrl = `https://www.bitget.site/fr/futures/usdt/${cleanSymbol}`;

                return `
                    <tr>
                        <td><strong>${pos.symbol}</strong></td>
                        <td><span class="badge badge-${pos.type.toLowerCase()}">${pos.type}</span></td>
                        <td>$${formatNumber(pos.entry_price)}</td>
                        <td>$${formatNumber(pos.current_price)}</td>
                        <td>$${formatNumber(pos.tp)}</td>
                        <td>$${formatNumber(pos.sl)}</td>
                        <td>$${formatNumber(pos.size_usdt, 2)}</td>
                        <td>${leverage}x</td>
                        <td class="${pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}">${formatCurrency(pnl)}</td>
                        <td class="${pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}">${formatPercent(pnlPercent)}</td>
                        <td>${calculateDuration(pos.opened_at)}</td>
                        <td>
                            <a href="${bitgetUrl}" target="_blank" class="btn-action bitget-link" title="Ouvrir sur Bitget">
                                <i class="fas fa-external-link-alt"></i> Bitget
                            </a>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // Historique
        const closedPositions = data.closed || [];
        if (closedPositions.length === 0) {
            elements.historyBody.innerHTML = '<tr><td colspan="12" class="no-data">Aucun trade fermé</td></tr>';
        } else {
            elements.historyBody.innerHTML = closedPositions.reverse().map(pos => {
                const pnl = pos.pnl_usdt || 0;
                const pnlPercent = pos.pnl_percent_on_margin || pos.pnl_percent || 0;
                const leverage = pos.leverage || 1;
                const closedDate = new Date(pos.closed_at).toLocaleString('fr-FR');

                let reasonEmoji = '✓';
                if (pos.close_reason === 'TP_HIT') reasonEmoji = '🎯';
                else if (pos.close_reason === 'SL_HIT') reasonEmoji = '🛑';
                else if (pos.close_reason === 'LIQUIDATED') reasonEmoji = '💀';

                // Générer l'URL Bitget pour cette paire (nettoyer le symbole en enlevant les /)
                const cleanSymbol = pos.symbol.replace('/', '');
                const bitgetUrl = `https://www.bitget.site/fr/futures/usdt/${cleanSymbol}`;

                return `
                    <tr>
                        <td>${closedDate}</td>
                        <td><strong>${pos.symbol}</strong></td>
                        <td><span class="badge badge-${pos.type.toLowerCase()}">${pos.type}</span></td>
                        <td>$${formatNumber(pos.entry_price)}</td>
                        <td>$${formatNumber(pos.exit_price)}</td>
                        <td>${reasonEmoji} ${pos.close_reason}</td>
                        <td>$${formatNumber(pos.size_usdt, 2)}</td>
                        <td>${leverage}x</td>
                        <td class="${pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}">${formatCurrency(pnl)}</td>
                        <td class="${pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}">${formatPercent(pnlPercent)}</td>
                        <td>${pos.duration_hours ? pos.duration_hours.toFixed(1) + 'h' : '-'}</td>
                        <td>
                            <a href="${bitgetUrl}" target="_blank" class="btn-action bitget-link" title="Ouvrir sur Bitget">
                                <i class="fas fa-external-link-alt"></i> Bitget
                            </a>
                        </td>
                    </tr>
                `;
            }).join('');
        }

    } catch (error) {
        console.error('Erreur lors de la mise à jour des positions:', error);
    }
}

// Mise à jour du statut du bot
async function updateBotStatus() {
    try {
        const response = await fetch('/api/bot/status');
        const status = await response.json();

        const isRunning = status.running;

        // Mise à jour de l'interface
        elements.botStatus.className = `bot-status ${isRunning ? 'running' : 'stopped'}`;
        elements.botStatusText.textContent = isRunning ? 'En cours d\'exécution' : 'Arrêté';

        elements.btnStart.disabled = isRunning;
        elements.btnStop.disabled = !isRunning;

    } catch (error) {
        console.error('Erreur lors de la mise à jour du statut:', error);
    }
}

// Mise à jour de la configuration
async function updateConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        // Trading config
        elements.configSymbols.textContent = config.symbols.join(', ');
        elements.configTimeframe.textContent = config.timeframe;
        elements.configInterval.textContent = `${config.check_interval} min`;
        elements.configScore.textContent = config.min_confidence_score;
        elements.configRR.textContent = `1:${config.min_risk_reward}`;

        // Paper trading
        const pt = config.paper_trading;
        elements.configPTEnabled.textContent = pt.enabled ? '✓ Oui' : '✗ Non';
        elements.configPTBalance.textContent = formatCurrency(pt.initial_balance);
        elements.configPTSize.textContent = `${pt.position_size_percent}%`;
        elements.configPTMax.textContent = pt.max_positions;
        elements.configPTLeverage.textContent = `${pt.leverage}x`;
        elements.configPTTrailingStop.textContent = pt.trailing_stop ? '✓ Oui' : '✗ Non';
        elements.configPTFixedTP.textContent = pt.fixed_tp ? '✓ Oui' : '✗ Non';
        elements.configPTTrailingTP.textContent = pt.trailing_tp ? '✓ Oui' : '✗ Non';

        // Trading hours
        const hours = config.trading_hours;
        elements.configHoursEnabled.textContent = hours.enabled ? '✓ Oui' : '✗ Non';
        elements.configHoursRange.textContent = `${hours.start}h - ${hours.end}h`;

        const daysNames = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
        const daysText = hours.days.map(d => daysNames[d]).join(', ');
        elements.configHoursDays.textContent = daysText;

    } catch (error) {
        console.error('Erreur lors de la mise à jour de la config:', error);
    }
}

// Mise à jour des logs
async function updateLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        const logs = data.logs || [];

        if (logs.length === 0) {
            elements.logsContainer.innerHTML = '<div class="no-data">Aucun log disponible</div>';
        } else {
            elements.logsContainer.innerHTML = logs.map(line =>
                `<div class="log-line">${line.trim()}</div>`
            ).join('');

            // Auto-scroll vers le bas
            elements.logsContainer.scrollTop = elements.logsContainer.scrollHeight;
        }

    } catch (error) {
        console.error('Erreur lors de la mise à jour des logs:', error);
    }
}

// Contrôles du bot
async function startBot() {
    try {
        elements.btnStart.disabled = true;
        elements.btnStart.innerHTML = '<span class="loading"></span> Démarrage...';

        const response = await fetch('/api/bot/start', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alert('✓ Bot démarré avec succès');
            await updateBotStatus();
        } else {
            alert('✗ Erreur: ' + result.message);
        }

    } catch (error) {
        alert('✗ Erreur lors du démarrage: ' + error.message);
    } finally {
        elements.btnStart.innerHTML = '▶ Démarrer';
        await updateBotStatus();
    }
}

async function stopBot() {
    try {
        elements.btnStop.disabled = true;
        elements.btnStop.innerHTML = '<span class="loading"></span> Arrêt...';

        const response = await fetch('/api/bot/stop', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alert('✓ Bot arrêté avec succès');
            await updateBotStatus();
        } else {
            alert('✗ Erreur: ' + result.message);
        }

    } catch (error) {
        alert('✗ Erreur lors de l\'arrêt: ' + error.message);
    } finally {
        elements.btnStop.innerHTML = '⏹ Arrêter';
        await updateBotStatus();
    }
}

// Mise à jour complète
async function refreshAll() {
    await Promise.all([
        updateStats(),
        updatePositions(),
        updateBotStatus(),
        updateLogs()
    ]);

    // Mise à jour de l'heure
    elements.lastUpdate.textContent = new Date().toLocaleTimeString('fr-FR');
}

// Fonction pour exporter les trades en CSV
function exportTradesToCSV() {
    const exportStatus = document.getElementById('export-status');
    const exportButton = document.getElementById('btn-export-csv');
    
    if (!exportStatus || !exportButton) {
        console.error('Éléments d\'export non trouvés');
        return;
    }
    
    exportStatus.textContent = 'Préparation de l\'export...';
    exportStatus.className = 'export-status';
    exportButton.disabled = true;
    
    fetch('/api/export/trades/csv')
        .then(response => {
            // Vérifier le content-type pour déterminer si c'est du JSON ou du CSV
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                // C'est une réponse JSON (erreur)
                return response.json().then(data => {
                    if (!response.ok) {
                        throw new Error(data.message || 'Aucun trade disponible');
                    }
                    return data;
                });
            } else if (response.ok) {
                // C'est un fichier CSV
                return response.blob();
            } else {
                // Autre type d'erreur
                throw new Error('Erreur serveur lors de l\'export');
            }
        })
        .then(result => {
            if (result instanceof Blob) {
                // Télécharger le fichier CSV
                const url = window.URL.createObjectURL(result);
                const a = document.createElement('a');
                a.href = url;
                a.download = `trades_export_${new Date().toISOString().slice(0, 10)}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                exportStatus.textContent = '✓ Export réussi !';
                exportStatus.className = 'export-status success';
            } else {
                // Cas inattendu
                console.error('Réponse inattendue:', result);
                throw new Error('Format de réponse inattendu');
            }
        })
        .catch(error => {
            console.error('Erreur export:', error);
            exportStatus.textContent = `✗ ${error.message}`;
            exportStatus.className = 'export-status error';
        })
        .finally(() => {
            setTimeout(() => {
                exportButton.disabled = false;
                exportStatus.textContent = '';
            }, 5000);
        });
}

// Initialisation
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Interface initialisée');

    // Event listeners
    elements.btnStart.addEventListener('click', startBot);
    elements.btnStop.addEventListener('click', stopBot);

    // Bouton de test des notifications
    const btnTestNotif = document.getElementById('btn-test-notif');
    if (btnTestNotif) {
        btnTestNotif.addEventListener('click', () => {
            if (window.notificationManager) {
                window.notificationManager.sendTestNotification();
            }
        });
    }

    // Bouton d'export CSV
    const btnExportCSV = document.getElementById('btn-export-csv');
    if (btnExportCSV) {
        btnExportCSV.addEventListener('click', exportTradesToCSV);
    }

    // Première mise à jour
    await refreshAll();
    await updateConfig();

    // Auto-refresh
    refreshTimer = setInterval(refreshAll, REFRESH_INTERVAL);

    console.log(`✓ Auto-refresh activé (${REFRESH_INTERVAL / 1000}s)`);
});

// Cleanup
window.addEventListener('beforeunload', () => {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
});
