from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

LINE_HEIGHT = 15
BLOCK_PADDING = 40
BOTTOM_MARGIN = 60
TOP_Y = 750
LEFT_X = 72


def _lines_for(stock, stock_metrics, comparison, backtest_summary, ml_results):
    m = stock_metrics[stock]
    c = comparison[stock]
    b = backtest_summary[stock]

    lines = [
        f"Total Return (5y):      {m['Total Return']:.2f}%",
        f"Avg Daily Return:       {m['Avg Daily Return']:.2f}%",
        f"Daily Volatility:       {m['Volatility']:.2f}%",
        f"Sharpe Ratio (ann.):    {m['Sharpe Ratio']:.2f}",
        f"Max Drawdown:           {m['Max Drawdown']:.2f}%",
        f"Beats benchmark return: {c['Beats Benchmark Return']}",
        f"Beats benchmark Sharpe: {c['Beats Sharpe Ratio']}",
        '',
        f"Backtest window: {b['n_days']} days from {b['start_date'].date()}",
        f"  Buy and hold:         {b['No Strategy Return']:.2f}x",
        f"  MA crossover:         {b['Strategy Return']:.2f}x"
        f"  (in market {b['Exposure']:.1%})",
    ]

    if ml_results and ml_results.get(stock):
        r = ml_results[stock]
        lines += [
            f"  Random forest:        {r['rf_return']:.2f}x"
            f"  (in market {r['rf_exposure']:.1%})",
            f"  Logistic regression:  {r['lr_return']:.2f}x"
            f"  (in market {r['lr_exposure']:.1%})",
            f"  Actual up days:       {r['base_rate']:.1%}",
        ]

    return lines


def generate_report(stock_metrics, comparison, backtest_summary, stocks,
                    ml_results=None, path='outputs/report.pdf'):
    c = canvas.Canvas(path, pagesize=letter)
    y = TOP_Y

    c.setFont('Helvetica-Bold', 16)
    c.drawString(LEFT_X, y, 'Stock Market Analyzer Report')
    y -= 30

    c.setFont('Helvetica', 9)
    c.drawString(LEFT_X, y, 'All strategy returns are measured over the same '
                            'window and are out-of-sample.')
    y -= 30

    for stock in stocks:
        lines = _lines_for(stock, stock_metrics, comparison,
                           backtest_summary, ml_results)

        # measure the block BEFORE drawing it, so a stock is never split
        # across a page break or run off the bottom
        block_height = LINE_HEIGHT * (len(lines) + 1) + BLOCK_PADDING

        if y - block_height < BOTTOM_MARGIN:
            c.showPage()
            y = TOP_Y

        c.setFont('Helvetica-Bold', 12)
        c.drawString(LEFT_X, y, stock)
        y -= 20

        c.setFont('Helvetica', 9.5)
        for line in lines:
            c.drawString(LEFT_X, y, line)
            y -= LINE_HEIGHT

        y -= 20

    c.save()