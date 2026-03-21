// static/js/app.js

// API Base URL
const API_URL = '/api';

// ============================================
// INDEX PAGE - Portfolio List
// ============================================

if (document.getElementById('create-portfolio-form')) {
    loadPortfolios();
    
    document.getElementById('create-portfolio-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('portfolio-name').value;
        const description = document.getElementById('portfolio-description').value;
        
        await createPortfolio(name, description);
    });
}

async function loadPortfolios() {
    try {
        const response = await fetch(`${API_URL}/portfolios`);
        const portfolios = await response.json();
        
        const container = document.getElementById('portfolios-list');
        
        if (portfolios.length === 0) {
            container.innerHTML = '<p class="empty-state">No portfolios yet. Create one to get started!</p>';
            return;
        }
        
        container.innerHTML = portfolios.map(p => `
            <div class="portfolio-card" onclick="window.location.href='/portfolio/${p.id}'">
                <h3>${p.name}</h3>
                <p>${p.description || 'No description'}</p>
                <div class="portfolio-card-footer">
                    <span class="portfolio-date">Created ${new Date(p.created_date).toLocaleDateString()}</span>
                    <button class="btn-danger" onclick="deletePortfolio(${p.id}, event)">Delete</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading portfolios:', error);
    }
}

async function createPortfolio(name, description) {
    try {
        const response = await fetch(`${API_URL}/portfolios`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, description })
        });
        
        if (response.ok) {
            document.getElementById('create-portfolio-form').reset();
            await loadPortfolios();
            alert('Portfolio created! 🎉');
        }
    } catch (error) {
        console.error('Error creating portfolio:', error);
        alert('Failed to create portfolio');
    }
}

async function deletePortfolio(portfolioId, event) {
    event.stopPropagation();
    
    if (!confirm('Delete this portfolio? This cannot be undone!')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/portfolios/${portfolioId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadPortfolios();
        }
    } catch (error) {
        console.error('Error deleting portfolio:', error);
    }
}

// ============================================
// PORTFOLIO DETAIL PAGE
// ============================================

if (typeof PORTFOLIO_ID !== 'undefined') {
    loadPortfolioDetail();
    
    // Set today's date as default
    document.getElementById('purchase-date').valueAsDate = new Date();
    
    document.getElementById('add-stock-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await addStock();
    });
}

let portfolioChart = null;

async function loadPortfolioDetail() {
    try {
        const response = await fetch(`${API_URL}/portfolios/${PORTFOLIO_ID}/summary`);
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            window.location.href = '/';
            return;
        }
        
        // Update header
        document.getElementById('portfolio-name').textContent = data.portfolio.name;
        
        // Update summary cards
        document.getElementById('total-cost').textContent = formatCurrency(data.total_cost);
        document.getElementById('total-value').textContent = formatCurrency(data.total_value);
        
        const gainElem = document.getElementById('total-gain');
        gainElem.textContent = formatCurrency(Math.abs(data.total_gain_loss));
        gainElem.className = 'amount ' + (data.total_gain_loss >= 0 ? 'gain' : 'loss');
        
        const percentElem = document.getElementById('total-percent');
        percentElem.textContent = data.total_gain_loss_percent.toFixed(2) + '%';
        percentElem.className = 'amount ' + (data.total_gain_loss >= 0 ? 'gain' : 'loss');
        
        // Render stocks table
        renderStocksTable(data.stocks);
        
        // Render chart
        renderChart(data.stocks);
        
    } catch (error) {
        console.error('Error loading portfolio:', error);
    }
}

function renderStocksTable(stocks) {
    const container = document.getElementById('stocks-list');
    
    if (stocks.length === 0) {
        container.innerHTML = '<p class="empty-state">No stocks yet. Add some to get started!</p>';
        return;
    }
    
    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Shares</th>
                    <th>Buy Price</th>
                    <th>Current Price</th>
                    <th>Total Cost</th>
                    <th>Current Value</th>
                    <th>Gain/Loss</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${stocks.map(stock => {
                    const gainClass = stock.gain_loss >= 0 ? 'gain' : 'loss';
                    const gainPrefix = stock.gain_loss >= 0 ? '+' : '';
                    
                    return `
                        <tr>
                            <td class="stock-symbol">${stock.symbol}</td>
                            <td class="stock-name">${stock.name}</td>
                            <td>${stock.shares.toFixed(2)}</td>
                            <td>${formatCurrency(stock.purchase_price)}</td>
                            <td>${formatCurrency(stock.current_price)}</td>
                            <td>${formatCurrency(stock.total_cost)}</td>
                            <td>${formatCurrency(stock.current_value)}</td>
                            <td class="${gainClass}">
                                ${gainPrefix}${formatCurrency(Math.abs(stock.gain_loss))}<br>
                                <small>(${gainPrefix}${stock.gain_loss_percent.toFixed(2)}%)</small>
                            </td>
                            <td>
                                <button class="btn-danger" onclick="deleteStock(${stock.id || 0})">Delete</button>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

function renderChart(stocks) {
    if (stocks.length === 0) return;
    
    const ctx = document.getElementById('portfolioChart').getContext('2d');
    
    if (portfolioChart) {
        portfolioChart.destroy();
    }
    
    portfolioChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: stocks.map(s => s.symbol),
            datasets: [{
                data: stocks.map(s => s.current_value),
                backgroundColor: [
                    '#667eea', '#f59e0b', '#10b981', '#ef4444',
                    '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${formatCurrency(context.parsed)}`;
                        }
                    }
                }
            }
        }
    });
}

async function addStock() {
    const symbol = document.getElementById('symbol').value.toUpperCase();
    const shares = parseFloat(document.getElementById('shares').value);
    const purchasePrice = parseFloat(document.getElementById('purchase-price').value);
    const purchaseDate = document.getElementById('purchase-date').value;
    
    try {
        const response = await fetch(`${API_URL}/portfolios/${PORTFOLIO_ID}/stocks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol,
                shares,
                purchase_price: purchasePrice,
                purchase_date: purchaseDate
            })
        });
        
        if (response.ok) {
            document.getElementById('add-stock-form').reset();
            document.getElementById('purchase-date').valueAsDate = new Date();
            await loadPortfolioDetail();
            alert('Stock added! 🎉');
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Failed to add stock'));
        }
    } catch (error) {
        console.error('Error adding stock:', error);
        alert('Failed to add stock');
    }
}

async function deleteStock(stockId) {
    if (!confirm('Remove this stock?')) return;
    
    try {
        const response = await fetch(`${API_URL}/portfolios/${PORTFOLIO_ID}/stocks/${stockId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadPortfolioDetail();
        }
    } catch (error) {
        console.error('Error deleting stock:', error);
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}