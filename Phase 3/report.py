from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors



def generate_report(stock_metrics, comparison, backtest_summary, stocks):
    c = canvas.Canvas('outputs/report.pdf', pagesize=letter)
    y = 750

    # Title
    c.setFont('Times-Bold', 16)
    c.drawString(100, y, 'Stock Market Analyzer Report')
    y -= 40

    # stock loop
    for stock in stocks:
        c.setFont('Helvetica-Bold', 12)
        c.drawString(100, y, f'--- {stock} ---')
        y -= 20

        c.setFont('Helvetica', 9.5)
        c.drawString(100, y, f"Total Return: {stock_metrics[stock]['Total Return']:.2f}%")
        y -= 15
        c.drawString(100, y, f"Avg Daily Return: {stock_metrics[stock]['Avg Daily Return']:.2f}%")
        y -= 15
        c.drawString(100, y, f"Volatility: {stock_metrics[stock]['Volatility']:.2f}%")
        y -= 15
        c.drawString(100, y, f"Sharpe Ratio: {stock_metrics[stock]['Sharpe Ratio']:.2f}")
        y -= 15
        c.drawString(100, y, f"Max Drawdown: {stock_metrics[stock]['Max Drawdown']:.2f}%")
        y -= 15
        c.drawString(100, y, f"Beats Benchmark Return: {comparison[stock]['Beats Benchmark Return']}")
        y -= 15
        c.drawString(100, y, f"Beats Benchmark Sharpe: {comparison[stock]['Beats Sharpe Ratio']}")
        y -= 15
        c.drawString(100, y, f"Strategy Return: {backtest_summary[stock]['Strategy Return']:.2f}x")
        y -= 15
        c.drawString(100, y, f"Buy and Hold Return: {backtest_summary[stock]['No Strategy Return']:.2f}x")
        y -= 15
        c.drawString(100, y, f"Strategy Beat Buy-and-Hold: {backtest_summary[stock]['Good Strategy']}")
        y -= 30
        if y < 250:
            c.showPage()
            y = 750

    c.save()