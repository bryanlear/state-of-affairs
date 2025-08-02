#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_latest_analysis():
    """Load the most recent technical analysis CSV file."""
    files = [f for f in os.listdir('.') if f.startswith('eu_auto_technical_analysis_') and f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No EU auto technical analysis CSV files found")
    
    latest_file = sorted(files)[-1]
    print(f"Loading data from: {latest_file}")
    
    df = pd.read_csv(latest_file)
    return df

def create_performance_chart(df):
    """Create performance comparison chart."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('European Auto Manufacturers - Performance Analysis', fontsize=16, fontweight='bold')
    
    # 3-Year Performance
    perf_data = df.sort_values('price_roc_3y', ascending=True)
    colors = ['red' if x < 0 else 'green' for x in perf_data['price_roc_3y']]
    
    ax1.barh(perf_data['symbol'], perf_data['price_roc_3y'], color=colors, alpha=0.7)
    ax1.set_xlabel('3-Year Return (%)')
    ax1.set_title('3-Year Performance Comparison')
    ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax1.grid(True, alpha=0.3)
    
    # YTD Performance
    ytd_data = df.sort_values('price_roc_ytd', ascending=True)
    colors = ['red' if x < 0 else 'green' for x in ytd_data['price_roc_ytd']]
    
    ax2.barh(ytd_data['symbol'], ytd_data['price_roc_ytd'], color=colors, alpha=0.7)
    ax2.set_xlabel('YTD Return (%)')
    ax2.set_title('Year-to-Date Performance')
    ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # Current Price vs 200-day SMA
    sma_data = df.sort_values('price_vs_sma200', ascending=True)
    colors = ['red' if x < 0 else 'green' for x in sma_data['price_vs_sma200']]
    
    ax3.barh(sma_data['symbol'], sma_data['price_vs_sma200'], color=colors, alpha=0.7)
    ax3.set_xlabel('Price vs 200-day SMA (%)')
    ax3.set_title('Technical Position (vs 200-day SMA)')
    ax3.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax3.grid(True, alpha=0.3)
    
    # Volatility
    vol_data = df.sort_values('volatility_30d', ascending=False)
    
    ax4.bar(vol_data['symbol'], vol_data['volatility_30d'], alpha=0.7, color='orange')
    ax4.set_ylabel('30-Day Volatility (%)')
    ax4.set_title('30-Day Volatility Comparison')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'eu_auto_performance_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Performance chart saved: {filename}")
    plt.show()

def create_volume_analysis_chart(df):
    """Create volume analysis chart."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('European Auto Manufacturers - Volume Analysis', fontsize=16, fontweight='bold')
    
    # Volume ROC 1-Day
    vol_roc_data = df.sort_values('volume_roc_1d', ascending=True)
    colors = ['red' if x < 0 else 'green' for x in vol_roc_data['volume_roc_1d']]
    
    ax1.barh(vol_roc_data['symbol'], vol_roc_data['volume_roc_1d'], color=colors, alpha=0.7)
    ax1.set_xlabel('1-Day Volume Change (%)')
    ax1.set_title('Daily Volume Rate of Change')
    ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax1.grid(True, alpha=0.3)
    
    # Volume vs Average
    vol_avg_data = df.sort_values('volume_vs_avg', ascending=True)
    colors = ['red' if x < 0 else 'green' for x in vol_avg_data['volume_vs_avg']]
    
    ax2.barh(vol_avg_data['symbol'], vol_avg_data['volume_vs_avg'], color=colors, alpha=0.7)
    ax2.set_xlabel('Volume vs 20-day Average (%)')
    ax2.set_title('Current Volume vs Average')
    ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # Average Volume (30-day)
    avg_vol_data = df.sort_values('avg_volume_30d', ascending=False)
    
    ax3.bar(avg_vol_data['symbol'], avg_vol_data['avg_volume_30d'] / 1e6, alpha=0.7, color='blue')
    ax3.set_ylabel('Average Volume (Millions)')
    ax3.set_title('30-Day Average Volume')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # Volume ROC vs Price ROC (1-month)
    ax4.scatter(df['volume_roc_1m'], df['price_roc_1m'], alpha=0.7, s=100)
    
    for i, row in df.iterrows():
        ax4.annotate(row['symbol'], (row['volume_roc_1m'], row['price_roc_1m']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax4.set_xlabel('1-Month Volume ROC (%)')
    ax4.set_ylabel('1-Month Price ROC (%)')
    ax4.set_title('Volume vs Price Momentum (1-Month)')
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax4.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'eu_auto_volume_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Volume analysis chart saved: {filename}")
    plt.show()

def create_risk_return_chart(df):
    """Create risk-return analysis chart."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('European Auto Manufacturers - Risk & Return Analysis', fontsize=16, fontweight='bold')
    
    # Risk-Return Scatter (3-year return vs volatility)
    ax1.scatter(df['volatility_30d'], df['price_roc_3y'], alpha=0.7, s=100, c=df['price_roc_3y'], 
               cmap='RdYlGn', vmin=-80, vmax=50)
    
    for i, row in df.iterrows():
        ax1.annotate(row['symbol'], (row['volatility_30d'], row['price_roc_3y']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax1.set_xlabel('30-Day Volatility (%)')
    ax1.set_ylabel('3-Year Return (%)')
    ax1.set_title('Risk vs Return (3-Year)')
    ax1.grid(True, alpha=0.3)
    
    # Price vs Moving Averages Heatmap
    ma_data = df[['symbol', 'price_vs_sma20', 'price_vs_sma50', 'price_vs_sma200']].set_index('symbol')
    ma_data.columns = ['vs 20-day', 'vs 50-day', 'vs 200-day']
    
    sns.heatmap(ma_data, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
                cbar_kws={'label': 'Price vs SMA (%)'}, ax=ax2)
    ax2.set_title('Price Position vs Moving Averages')
    ax2.set_ylabel('')
    
    # Performance Comparison (Multiple timeframes)
    perf_data = df[['symbol', 'price_roc_1d', 'price_roc_1m', 'price_roc_ytd', 'price_roc_3y']].set_index('symbol')
    perf_data.columns = ['1-Day', '1-Month', 'YTD', '3-Year']
    
    sns.heatmap(perf_data, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                cbar_kws={'label': 'Return (%)'}, ax=ax3)
    ax3.set_title('Performance Across Timeframes')
    ax3.set_ylabel('')
    
    # Current Price Distribution
    ax4.hist(df['current_price'], bins=8, alpha=0.7, color='skyblue', edgecolor='black')
    ax4.set_xlabel('Current Price ($)')
    ax4.set_ylabel('Number of Stocks')
    ax4.set_title('Current Price Distribution')
    ax4.grid(True, alpha=0.3)

    for price in df['current_price']:
        ax4.axvline(x=price, color='red', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'eu_auto_risk_return_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Risk-return analysis chart saved: {filename}")
    plt.show()

def create_summary_dashboard(df):
    """Create a comprehensive summary dashboard."""
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    fig.suptitle('European Auto Manufacturers - Technical Analysis Dashboard', fontsize=20, fontweight='bold')
    
    # 1. 3-Year Performance (Top Left)
    ax1 = fig.add_subplot(gs[0, :2])
    perf_data = df.sort_values('price_roc_3y', ascending=True)
    colors = ['red' if x < 0 else 'green' for x in perf_data['price_roc_3y']]
    bars = ax1.barh(perf_data['symbol'], perf_data['price_roc_3y'], color=colors, alpha=0.7)
    ax1.set_xlabel('3-Year Return (%)')
    ax1.set_title('3-Year Performance Ranking', fontweight='bold')
    ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars, perf_data['price_roc_3y']):
        ax1.text(value + (1 if value >= 0 else -1), bar.get_y() + bar.get_height()/2, 
                f'{value:.1f}%', ha='left' if value >= 0 else 'right', va='center', fontsize=9)
    
    # 2. Current Technical Position (Top Right)
    ax2 = fig.add_subplot(gs[0, 2:])
    sma_data = df.sort_values('price_vs_sma200', ascending=True)
    colors = ['red' if x < 0 else 'green' for x in sma_data['price_vs_sma200']]
    bars = ax2.barh(sma_data['symbol'], sma_data['price_vs_sma200'], color=colors, alpha=0.7)
    ax2.set_xlabel('Price vs 200-day SMA (%)')
    ax2.set_title('Technical Position (vs 200-day SMA)', fontweight='bold')
    ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # 3. Risk-Return Scatter (Middle Left)
    ax3 = fig.add_subplot(gs[1, :2])
    scatter = ax3.scatter(df['volatility_30d'], df['price_roc_ytd'], 
                         alpha=0.7, s=150, c=df['price_roc_3y'], cmap='RdYlGn', vmin=-80, vmax=50)
    
    for i, row in df.iterrows():
        ax3.annotate(row['symbol'], (row['volatility_30d'], row['price_roc_ytd']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
    
    ax3.set_xlabel('30-Day Volatility (%)')
    ax3.set_ylabel('YTD Return (%)')
    ax3.set_title('Risk vs YTD Return (Color = 3Y Return)', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax3, label='3-Year Return (%)')
    
    # 4. Volume Analysis (Middle Right)
    ax4 = fig.add_subplot(gs[1, 2:])
    vol_data = df.sort_values('avg_volume_30d', ascending=False)
    bars = ax4.bar(vol_data['symbol'], vol_data['avg_volume_30d'] / 1e6, alpha=0.7, color='blue')
    ax4.set_ylabel('Average Volume (Millions)')
    ax4.set_title('30-Day Average Trading Volume', fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # 5. Performance Heatmap (Bottom)
    ax5 = fig.add_subplot(gs[2, :])
    perf_matrix = df[['symbol', 'price_roc_1d', 'price_roc_1m', 'price_roc_ytd', 'price_roc_3y']].set_index('symbol')
    perf_matrix.columns = ['1-Day (%)', '1-Month (%)', 'YTD (%)', '3-Year (%)']
    
    sns.heatmap(perf_matrix, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                cbar_kws={'label': 'Return (%)'}, ax=ax5, linewidths=0.5)
    ax5.set_title('Performance Matrix Across All Timeframes', fontweight='bold')
    ax5.set_ylabel('')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'eu_auto_technical_dashboard_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Technical analysis dashboard saved: {filename}")
    plt.show()

def main():
    """Main function to create all charts."""
    try:
        print("Creating Technical Analysis Charts")
        print("=================================")
 
        df = load_latest_analysis()
        print(f"Loaded data for {len(df)} stocks")
 
        print("\n1. Creating performance analysis chart...")
        create_performance_chart(df)
        
        print("\n2. Creating volume analysis chart...")
        create_volume_analysis_chart(df)
        
        print("\n3. Creating risk-return analysis chart...")
        create_risk_return_chart(df)
        
        print("\n4. Creating comprehensive dashboard...")
        create_summary_dashboard(df)
        
        print("\n✅ All charts created successfully!")
        
    except Exception as e:
        print(f"Error creating charts: {e}")

if __name__ == "__main__":
    main()
