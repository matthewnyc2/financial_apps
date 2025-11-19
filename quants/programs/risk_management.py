"""
Risk Management Implementation
Includes Historical VaR, Parametric VaR, Monte Carlo VaR, CVaR/Expected Shortfall,
stress testing, scenario analysis, and correlation analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, t as t_dist
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class RiskMetrics:
    """
    Comprehensive risk management class supporting multiple VaR methodologies
    and advanced risk metrics
    """

    def __init__(self, returns_data, price_data=None, confidence_level=0.95):
        """
        Initialize with returns data and optional price data

        Parameters:
        -----------
        returns_data : pd.Series or np.array
            Log returns or simple returns (in decimal form, e.g., 0.01 for 1%)
        price_data : pd.Series or np.array, optional
            Asset prices for P&L calculations
        confidence_level : float
            Confidence level for VaR calculations (default: 0.95 for 95% VaR)
        """
        if isinstance(returns_data, pd.Series):
            self.returns = returns_data
        else:
            self.returns = pd.Series(returns_data)

        self.price_data = price_data
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level  # Quantile level (e.g., 0.05 for 95% VaR)

        # Pre-calculate statistics
        self.mean_return = self.returns.mean()
        self.std_return = self.returns.std()
        self.skewness = self.returns.skew()
        self.kurtosis = self.returns.kurtosis()

    # ==================== HISTORICAL VaR ====================

    def var_historical(self, portfolio_value=1.0, period=1):
        """
        Historical VaR using empirical quantile of returns distribution

        VaR_historical = -percentile(returns, α)

        where α is the significance level (e.g., 0.05 for 95% VaR)

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value (default: 1.0 for percentage VaR)
        period : int
            Time horizon in days (default: 1-day VaR)

        Returns:
        --------
        dict : VaR value and loss in dollars

        Mathematical Formula:
        VaR(α) = -quantile_α(X)
        where X is the return distribution
        """
        # Scale returns to desired period (assuming √t scaling)
        scaled_returns = self.returns * np.sqrt(period)

        # Calculate historical VaR as negative quantile
        var_quantile = np.percentile(scaled_returns, self.alpha * 100)
        var_value = -var_quantile

        # Dollar loss
        dollar_loss = var_value * portfolio_value

        return {
            'VaR': var_value,
            'Dollar_Loss': dollar_loss,
            'Confidence_Level': self.confidence_level,
            'Period': period
        }

    def var_historical_alternative(self, portfolio_value=1.0, period=1):
        """
        Alternative historical VaR calculation using sorted returns
        More direct approach by sorting actual returns
        """
        scaled_returns = self.returns * np.sqrt(period)
        sorted_returns = np.sort(scaled_returns)

        # Index for the α-quantile
        index = int(len(sorted_returns) * self.alpha)
        var_value = -sorted_returns[index]

        dollar_loss = var_value * portfolio_value

        return {
            'VaR': var_value,
            'Dollar_Loss': dollar_loss,
            'Method': 'Sorted Returns',
            'Observations': len(sorted_returns)
        }

    # ==================== PARAMETRIC VaR ====================

    def var_parametric_normal(self, portfolio_value=1.0, period=1):
        """
        Parametric VaR assuming normal distribution

        VaR = μ + σ * Z_α

        where:
        - μ: mean return
        - σ: standard deviation
        - Z_α: α-quantile of standard normal distribution

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon in days

        Returns:
        --------
        dict : VaR value and confidence interval

        Mathematical Formula:
        VaR_normal(α) = -(μ + σ * Φ^(-1)(α))
        where Φ^(-1) is the inverse of standard normal CDF
        """
        # Annualized statistics
        mean_annual = self.mean_return * 252
        std_annual = self.std_return * np.sqrt(252)

        # Period adjustment
        mean_period = mean_annual * (period / 252)
        std_period = std_annual * np.sqrt(period / 252)

        # Normal quantile
        z_alpha = norm.ppf(self.alpha)

        # VaR calculation
        var_value = -(mean_period + std_period * z_alpha)
        dollar_loss = var_value * portfolio_value

        return {
            'VaR': var_value,
            'Dollar_Loss': dollar_loss,
            'Mean': mean_period,
            'Std_Dev': std_period,
            'Z_Score': z_alpha,
            'Method': 'Normal Distribution'
        }

    def var_parametric_student_t(self, portfolio_value=1.0, period=1):
        """
        Parametric VaR assuming Student's t distribution
        Better captures fat tails than normal distribution

        VaR = μ + σ * t_α(df)

        where t_α(df) is the α-quantile of Student's t with df degrees of freedom

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon in days

        Returns:
        --------
        dict : VaR value with tail risk adjustment

        Mathematical Formula:
        VaR_student_t(α) = -(μ + σ * t_α^(-1)(α, df))
        where t_α^(-1) is the inverse CDF of Student's t distribution
        """
        # Annualized statistics
        mean_annual = self.mean_return * 252
        std_annual = self.std_return * np.sqrt(252)

        # Period adjustment
        mean_period = mean_annual * (period / 252)
        std_period = std_annual * np.sqrt(period / 252)

        # Estimate degrees of freedom from kurtosis
        df = self._estimate_df_from_kurtosis()

        # Student's t quantile
        t_alpha = t_dist.ppf(self.alpha, df)

        # VaR calculation
        var_value = -(mean_period + std_period * t_alpha)
        dollar_loss = var_value * portfolio_value

        return {
            'VaR': var_value,
            'Dollar_Loss': dollar_loss,
            'Mean': mean_period,
            'Std_Dev': std_period,
            'T_Score': t_alpha,
            'Degrees_of_Freedom': df,
            'Method': 'Student t Distribution'
        }

    def var_parametric_cornish_fisher(self, portfolio_value=1.0, period=1):
        """
        Cornish-Fisher VaR using higher moments (skewness and kurtosis)
        More accurate for non-normal distributions with fat tails and skewness

        z_cf = z + (1/6)*z^2*(skew) + (1/24)*(z^3 - 3z)*(kurt - 3)
        VaR = μ + σ * z_cf

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon in days

        Returns:
        --------
        dict : VaR with skewness and kurtosis adjustments

        Mathematical Formula:
        z_CF(S, K) = z_α + (1/6)*z_α^2*S + (1/24)*(z_α^3 - 3z_α)*(K-3) - (1/36)*z_α^3*S^2
        where S = skewness, K = kurtosis
        """
        # Annualized statistics
        mean_annual = self.mean_return * 252
        std_annual = self.std_return * np.sqrt(252)

        # Period adjustment
        mean_period = mean_annual * (period / 252)
        std_period = std_annual * np.sqrt(period / 252)

        # Normal quantile
        z_alpha = norm.ppf(self.alpha)

        # Cornish-Fisher adjustment
        S = self.skewness
        K = self.kurtosis

        z_cf = (z_alpha +
                (1/6) * z_alpha**2 * S +
                (1/24) * (z_alpha**3 - 3*z_alpha) * (K - 3) -
                (1/36) * z_alpha**3 * S**2)

        # VaR calculation
        var_value = -(mean_period + std_period * z_cf)
        dollar_loss = var_value * portfolio_value

        return {
            'VaR': var_value,
            'Dollar_Loss': dollar_loss,
            'Mean': mean_period,
            'Std_Dev': std_period,
            'Cornish_Fisher_Z': z_cf,
            'Skewness': S,
            'Kurtosis': K,
            'Method': 'Cornish-Fisher'
        }

    # ==================== MONTE CARLO VaR ====================

    def var_monte_carlo(self, portfolio_value=1.0, period=1,
                       num_simulations=10000, seed=None):
        """
        Monte Carlo VaR using simulated returns
        Assumes returns follow a geometric Brownian motion

        dS/S = μ*dt + σ*dW

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon in days
        num_simulations : int
            Number of Monte Carlo paths
        seed : int
            Random seed for reproducibility

        Returns:
        --------
        dict : VaR value and simulation statistics

        Mathematical Formula:
        S_t = S_0 * exp((μ - σ^2/2)*t + σ*√t*Z)
        where Z ~ N(0,1)
        """
        if seed is not None:
            np.random.seed(seed)

        # Annualized parameters
        mu = self.mean_return * 252
        sigma = self.std_return * np.sqrt(252)

        # Time in years
        t = period / 252

        # Generate random normal shocks
        Z = np.random.standard_normal((num_simulations, max(1, period)))

        # Simulate returns using geometric Brownian motion
        # For single period: R = exp((μ - σ^2/2)*t + σ*√t*Z) - 1
        if period == 1:
            simulated_returns = np.exp((mu - sigma**2/2)*t + sigma*np.sqrt(t)*Z.flatten()) - 1
        else:
            # Multi-period simulation
            simulated_returns = np.zeros(num_simulations)
            S = 1.0
            for step in range(period):
                dt = 1/252
                dS = (mu*dt + sigma*np.sqrt(dt)*Z[:, step]) * S
                S = S + dS
            simulated_returns = S - 1

        # Calculate VaR from simulated returns
        var_quantile = np.percentile(simulated_returns, self.alpha * 100)
        var_value = -var_quantile

        dollar_loss = var_value * portfolio_value

        # Additional statistics
        return {
            'VaR': var_value,
            'Dollar_Loss': dollar_loss,
            'Mean_Simulated': simulated_returns.mean(),
            'Std_Simulated': simulated_returns.std(),
            'Min_Return': simulated_returns.min(),
            'Max_Return': simulated_returns.max(),
            'Num_Simulations': num_simulations,
            'Method': 'Monte Carlo'
        }

    def var_monte_carlo_historical_bootstrap(self, portfolio_value=1.0,
                                              period=1, num_simulations=10000,
                                              seed=None):
        """
        Monte Carlo VaR using historical bootstrap
        Resamples from actual historical returns with replacement
        Non-parametric approach - makes no distribution assumptions

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Multi-period holding horizon
        num_simulations : int
            Number of simulations
        seed : int
            Random seed

        Returns:
        --------
        dict : VaR from bootstrap simulation

        Mathematical Formula:
        Sample returns with replacement from empirical distribution
        R_sim ~ bootstrap(R_historical)
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate simulated returns by bootstrapping
        simulated_returns = np.zeros(num_simulations)

        for sim in range(num_simulations):
            # Sample 'period' returns with replacement
            sampled_returns = np.random.choice(self.returns, size=period, replace=True)
            # Compound returns over period
            simulated_returns[sim] = np.prod(1 + sampled_returns) - 1

        # Calculate VaR
        var_quantile = np.percentile(simulated_returns, self.alpha * 100)
        var_value = -var_quantile

        dollar_loss = var_value * portfolio_value

        return {
            'VaR': var_value,
            'Dollar_Loss': dollar_loss,
            'Mean_Simulated': simulated_returns.mean(),
            'Std_Simulated': simulated_returns.std(),
            'Method': 'Historical Bootstrap',
            'Num_Simulations': num_simulations
        }

    # ==================== CVaR / Expected Shortfall ====================

    def cvar_historical(self, portfolio_value=1.0, period=1):
        """
        CVaR/Expected Shortfall (ES) using historical data
        Average loss conditioned on exceeding VaR

        CVaR = E[L | L > VaR]

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon

        Returns:
        --------
        dict : CVaR value and loss

        Mathematical Formula:
        CVaR_α = E[X | X ≤ F^(-1)(α)]
        Average of returns below the α-quantile
        """
        # Get VaR first
        var_result = self.var_historical(portfolio_value=1.0, period=period)
        var_value = var_result['VaR']

        # Scale returns
        scaled_returns = self.returns * np.sqrt(period)

        # Find losses exceeding VaR
        losses = -scaled_returns
        losses_exceeding_var = losses[losses > var_value]

        # CVaR is the mean of losses exceeding VaR
        cvar_value = losses_exceeding_var.mean() if len(losses_exceeding_var) > 0 else var_value

        dollar_loss = cvar_value * portfolio_value

        return {
            'CVaR': cvar_value,
            'Dollar_Loss': dollar_loss,
            'VaR': var_value,
            'Observations_in_Tail': len(losses_exceeding_var),
            'Method': 'Historical',
            'Confidence_Level': self.confidence_level
        }

    def cvar_parametric_normal(self, portfolio_value=1.0, period=1):
        """
        CVaR assuming normal distribution

        CVaR = μ + σ * φ(Z_α) / α

        where φ is the standard normal PDF

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon

        Returns:
        --------
        dict : CVaR with normal distribution assumption

        Mathematical Formula:
        CVaR_normal(α) = -(μ + σ * φ(Φ^(-1)(α)) / α)
        where φ is standard normal PDF, Φ^(-1) is inverse CDF
        """
        # Annualized statistics
        mean_annual = self.mean_return * 252
        std_annual = self.std_return * np.sqrt(252)

        # Period adjustment
        mean_period = mean_annual * (period / 252)
        std_period = std_annual * np.sqrt(period / 252)

        # Normal quantile
        z_alpha = norm.ppf(self.alpha)

        # Normal PDF at quantile
        pdf_z = norm.pdf(z_alpha)

        # CVaR calculation
        cvar_value = -(mean_period + std_period * pdf_z / self.alpha)
        dollar_loss = cvar_value * portfolio_value

        return {
            'CVaR': cvar_value,
            'Dollar_Loss': dollar_loss,
            'Mean': mean_period,
            'Std_Dev': std_period,
            'Z_Score': z_alpha,
            'Method': 'Normal Distribution'
        }

    def cvar_parametric_student_t(self, portfolio_value=1.0, period=1):
        """
        CVaR assuming Student's t distribution
        Better captures tail risk for non-normal distributions

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon

        Returns:
        --------
        dict : CVaR with Student's t distribution
        """
        # Annualized statistics
        mean_annual = self.mean_return * 252
        std_annual = self.std_return * np.sqrt(252)

        # Period adjustment
        mean_period = mean_annual * (period / 252)
        std_period = std_annual * np.sqrt(period / 252)

        # Estimate degrees of freedom
        df = self._estimate_df_from_kurtosis()

        # Student's t quantile
        t_alpha = t_dist.ppf(self.alpha, df)

        # PDF at quantile
        pdf_t = t_dist.pdf(t_alpha, df)

        # CVaR calculation
        cvar_value = -(mean_period + std_period * pdf_t / self.alpha)
        dollar_loss = cvar_value * portfolio_value

        return {
            'CVaR': cvar_value,
            'Dollar_Loss': dollar_loss,
            'Mean': mean_period,
            'Std_Dev': std_period,
            'T_Score': t_alpha,
            'Degrees_of_Freedom': df,
            'Method': 'Student t Distribution'
        }

    def cvar_monte_carlo(self, portfolio_value=1.0, period=1,
                        num_simulations=10000, seed=None):
        """
        CVaR from Monte Carlo simulations
        Average loss in the tail of simulated return distribution

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon
        num_simulations : int
            Number of simulations
        seed : int
            Random seed

        Returns:
        --------
        dict : CVaR from Monte Carlo
        """
        # Generate Monte Carlo returns
        mc_result = self.var_monte_carlo(portfolio_value=1.0, period=period,
                                         num_simulations=num_simulations, seed=seed)

        # Recalculate to get returns
        if seed is not None:
            np.random.seed(seed)

        mu = self.mean_return * 252
        sigma = self.std_return * np.sqrt(252)
        t = period / 252

        Z = np.random.standard_normal(num_simulations)
        simulated_returns = np.exp((mu - sigma**2/2)*t + sigma*np.sqrt(t)*Z) - 1

        # Find losses exceeding VaR
        losses = -simulated_returns
        var_value = np.percentile(losses, self.confidence_level * 100)

        # CVaR is mean of losses exceeding VaR
        cvar_value = losses[losses >= var_value].mean()

        dollar_loss = cvar_value * portfolio_value

        return {
            'CVaR': cvar_value,
            'Dollar_Loss': dollar_loss,
            'VaR': var_value,
            'Method': 'Monte Carlo',
            'Num_Simulations': num_simulations
        }

    # ==================== STRESS TESTING ====================

    def stress_test_absolute(self, stress_return, portfolio_value=1.0):
        """
        Stress test with absolute return shock
        What is the portfolio loss if market moves by X%?

        Parameters:
        -----------
        stress_return : float
            Absolute return shock (e.g., -0.10 for -10% market move)
        portfolio_value : float
            Portfolio value

        Returns:
        --------
        dict : Loss under stress scenario

        Mathematical Formula:
        Loss = Portfolio_Value × Stress_Return
        """
        loss = portfolio_value * stress_return

        return {
            'Stress_Return': stress_return,
            'Portfolio_Value': portfolio_value,
            'Loss': loss,
            'Loss_Percentage': stress_return,
            'Method': 'Absolute Shock'
        }

    def stress_test_relative_to_historical(self, stress_multiple, portfolio_value=1.0):
        """
        Stress test relative to historical volatility
        What is portfolio loss if volatility shock is X times historical std?

        Parameters:
        -----------
        stress_multiple : float
            Multiple of historical std (e.g., 3.0 for 3-sigma event)
        portfolio_value : float
            Portfolio value

        Returns:
        --------
        dict : Loss under volatility stress

        Mathematical Formula:
        Stress_Return = -stress_multiple × σ_historical
        Loss = Portfolio_Value × Stress_Return
        """
        stress_return = -stress_multiple * self.std_return * np.sqrt(252)
        loss = portfolio_value * stress_return

        return {
            'Stress_Multiple_Sigma': stress_multiple,
            'Historical_Annual_Std': self.std_return * np.sqrt(252),
            'Stress_Return': stress_return,
            'Loss': loss,
            'Portfolio_Value': portfolio_value,
            'Method': 'Relative to Volatility'
        }

    def stress_test_historical_scenarios(self, portfolio_value=1.0,
                                         percentile_losses=[5, 10, 25]):
        """
        Stress test using worst historical returns
        What were the worst historical days and their impact?

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        percentile_losses : list
            Historical percentiles to report (e.g., [5, 10, 25] for worst 5%, 10%, 25%)

        Returns:
        --------
        dict : Losses under worst historical scenarios

        Mathematical Formula:
        Loss = Portfolio_Value × Historical_Return_at_Percentile
        """
        scenarios = {}

        for percentile in percentile_losses:
            stress_return = np.percentile(self.returns, percentile)
            loss = portfolio_value * stress_return

            scenarios[f'Percentile_{percentile}'] = {
                'Return': stress_return,
                'Loss': loss,
                'Date': self.returns.idxmin() if percentile == 5 else None
            }

        return {
            'Scenarios': scenarios,
            'Worst_Daily_Return': self.returns.min(),
            'Worst_Daily_Loss': portfolio_value * self.returns.min(),
            'Portfolio_Value': portfolio_value,
            'Method': 'Historical Scenarios'
        }

    def stress_test_correlation_breakdown(self, correlation_matrix,
                                          correlations_under_stress,
                                          portfolio_weights,
                                          stress_volatility_multiplier=3.0):
        """
        Stress test with correlation breakdown
        What if correlations change during stress (typically increase)?

        Parameters:
        -----------
        correlation_matrix : np.array or pd.DataFrame
            Normal correlation matrix
        correlations_under_stress : np.array or pd.DataFrame
            Correlation matrix under stress (usually higher)
        portfolio_weights : np.array or pd.Series
            Asset weights
        stress_volatility_multiplier : float
            Volatility multiplier during stress

        Returns:
        --------
        dict : Portfolio risk metrics under correlation breakdown
        """
        if isinstance(portfolio_weights, pd.Series):
            weights = portfolio_weights.values
        else:
            weights = np.array(portfolio_weights)

        # Normalize weights
        weights = weights / weights.sum()

        # Normal volatilities
        daily_vols = self.returns.std()
        annual_vols = daily_vols * np.sqrt(252)

        # Stressed volatilities
        stressed_vols = annual_vols * stress_volatility_multiplier

        # Convert correlations to covariances
        normal_cov = correlation_matrix * np.outer(annual_vols, annual_vols)
        stressed_cov = correlations_under_stress * np.outer(stressed_vols, stressed_vols)

        # Portfolio variance
        normal_var = weights @ normal_cov @ weights
        stressed_var = weights @ stressed_cov @ weights

        normal_vol = np.sqrt(normal_var)
        stressed_vol = np.sqrt(stressed_var)

        return {
            'Normal_Portfolio_Vol': normal_vol,
            'Stressed_Portfolio_Vol': stressed_vol,
            'Vol_Increase': stressed_vol - normal_vol,
            'Vol_Increase_Percentage': (stressed_vol / normal_vol - 1) * 100,
            'Normal_Correlation_Mean': correlation_matrix[np.triu_indices_from(correlation_matrix, k=1)].mean(),
            'Stressed_Correlation_Mean': correlations_under_stress[np.triu_indices_from(correlations_under_stress, k=1)].mean(),
            'Method': 'Correlation Breakdown'
        }

    def reverse_stress_test(self, acceptable_loss, portfolio_value=1.0):
        """
        Reverse stress test: How bad does market need to move to hit acceptable loss?

        Parameters:
        -----------
        acceptable_loss : float
            Maximum acceptable loss (in dollars)
        portfolio_value : float
            Portfolio value

        Returns:
        --------
        dict : Required market move to hit acceptable loss

        Mathematical Formula:
        Required_Return = -Acceptable_Loss / Portfolio_Value
        """
        required_return = -acceptable_loss / portfolio_value

        # Express in terms of standard deviations
        annual_std = self.std_return * np.sqrt(252)
        sigma_move = required_return / annual_std

        return {
            'Acceptable_Loss': acceptable_loss,
            'Portfolio_Value': portfolio_value,
            'Required_Return': required_return,
            'Required_Return_Percentage': required_return * 100,
            'Sigma_Move': sigma_move,
            'Historical_Annual_Vol': annual_std,
            'Method': 'Reverse Stress Test'
        }

    # ==================== SCENARIO ANALYSIS ====================

    def scenario_analysis(self, scenarios_dict, portfolio_value=1.0):
        """
        Scenario analysis: Calculate portfolio impact for specified scenarios

        Parameters:
        -----------
        scenarios_dict : dict
            Dictionary mapping scenario names to return values
            Example: {'Bull_Case': 0.15, 'Base_Case': 0.05, 'Bear_Case': -0.10}
        portfolio_value : float
            Portfolio value

        Returns:
        --------
        dict : Portfolio P&L for each scenario

        Mathematical Formula:
        P&L_scenario = Portfolio_Value × Scenario_Return
        """
        results = {}

        for scenario_name, return_value in scenarios_dict.items():
            pnl = portfolio_value * return_value
            results[scenario_name] = {
                'Return': return_value,
                'Return_Percentage': return_value * 100,
                'P&L': pnl,
                'Portfolio_Value': portfolio_value
            }

        return {
            'Scenarios': results,
            'Best_Case': max([v['P&L'] for v in results.values()]),
            'Worst_Case': min([v['P&L'] for v in results.values()]),
            'Case_Range': max([v['P&L'] for v in results.values()]) - min([v['P&L'] for v in results.values()]),
            'Method': 'Scenario Analysis'
        }

    def scenario_analysis_macro(self, macro_scenarios_dict, asset_sensitivities):
        """
        Macro scenario analysis: Impact of macro factors on portfolio

        Parameters:
        -----------
        macro_scenarios_dict : dict
            Macro scenarios and their probabilities
            Example: {'Recession': 0.20, 'Slow_Growth': 0.50, 'Expansion': 0.30}
        asset_sensitivities : dict
            Asset returns for each macro scenario
            Example: {'Recession': {'Stock': -0.15, 'Bond': 0.05, 'Gold': 0.10}}

        Returns:
        --------
        dict : Expected portfolio return and risk under macro scenarios
        """
        results = {}
        expected_return = 0.0
        variance_components = []

        for scenario_name, probability in macro_scenarios_dict.items():
            asset_returns = asset_sensitivities.get(scenario_name, {})

            results[scenario_name] = {
                'Probability': probability,
                'Asset_Returns': asset_returns,
                'Scenario_Contribution': probability * np.mean(list(asset_returns.values()))
            }

            expected_return += results[scenario_name]['Scenario_Contribution']

        return {
            'Macro_Scenarios': results,
            'Expected_Return': expected_return,
            'Method': 'Macro Scenario Analysis'
        }

    # ==================== CORRELATION ANALYSIS ====================

    def correlation_analysis(self, asset_returns_dict):
        """
        Calculate and analyze correlations between assets

        Parameters:
        -----------
        asset_returns_dict : dict
            Dictionary of asset names to return series

        Returns:
        --------
        dict : Correlation matrix and analysis

        Mathematical Formula:
        ρ(X,Y) = Cov(X,Y) / (σ_X * σ_Y)
        """
        # Create DataFrame from dict
        returns_df = pd.DataFrame(asset_returns_dict)

        # Calculate correlation matrix
        corr_matrix = returns_df.corr()

        # Calculate covariance matrix
        cov_matrix = returns_df.cov()

        # Extract upper triangle for summary statistics
        corr_values = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)]

        analysis = {
            'Correlation_Matrix': corr_matrix,
            'Covariance_Matrix': cov_matrix,
            'Mean_Correlation': corr_values.mean(),
            'Min_Correlation': corr_values.min(),
            'Max_Correlation': corr_values.max(),
            'Std_Correlation': corr_values.std(),
            'Asset_Std_Dev': returns_df.std(),
            'Asset_Mean_Return': returns_df.mean()
        }

        return analysis

    def correlation_breakdown_analysis(self, asset_returns_dict,
                                       crisis_period_start=None,
                                       crisis_period_end=None):
        """
        Analyze how correlations change during crisis periods
        Correlations typically increase during stress

        Parameters:
        -----------
        asset_returns_dict : dict
            Dictionary of asset names to return series (must be pd.Series with DatetimeIndex)
        crisis_period_start : str or datetime
            Start date of crisis period
        crisis_period_end : str or datetime
            End date of crisis period

        Returns:
        --------
        dict : Correlation analysis for normal vs crisis periods
        """
        returns_df = pd.DataFrame(asset_returns_dict)

        # Normal period correlation
        normal_corr = returns_df.corr()

        # Crisis period correlation
        if crisis_period_start and crisis_period_end:
            crisis_returns = returns_df[crisis_period_start:crisis_period_end]
            crisis_corr = crisis_returns.corr()
        else:
            crisis_corr = None

        # Calculate changes
        if crisis_corr is not None:
            corr_change = crisis_corr - normal_corr

            results = {
                'Normal_Correlation_Mean': normal_corr.values[np.triu_indices_from(normal_corr.values, k=1)].mean(),
                'Crisis_Correlation_Mean': crisis_corr.values[np.triu_indices_from(crisis_corr.values, k=1)].mean(),
                'Correlation_Increase': crisis_corr.values[np.triu_indices_from(crisis_corr.values, k=1)].mean() - normal_corr.values[np.triu_indices_from(normal_corr.values, k=1)].mean(),
                'Normal_Correlation_Matrix': normal_corr,
                'Crisis_Correlation_Matrix': crisis_corr,
                'Correlation_Change_Matrix': corr_change
            }
        else:
            results = {
                'Normal_Correlation_Mean': normal_corr.values[np.triu_indices_from(normal_corr.values, k=1)].mean(),
                'Normal_Correlation_Matrix': normal_corr
            }

        return results

    def portfolio_risk_decomposition(self, asset_returns_dict, portfolio_weights):
        """
        Decompose portfolio risk into asset contributions

        Parameters:
        -----------
        asset_returns_dict : dict
            Dictionary of asset names to return series
        portfolio_weights : dict or np.array
            Portfolio weights by asset

        Returns:
        --------
        dict : Risk contribution by asset

        Mathematical Formula:
        Risk_Contribution_i = w_i * (Cov_Matrix @ weights)_i / Portfolio_Std_Dev
        """
        returns_df = pd.DataFrame(asset_returns_dict)

        # Get weights as array
        if isinstance(portfolio_weights, dict):
            weights = np.array([portfolio_weights[asset] for asset in returns_df.columns])
        else:
            weights = np.array(portfolio_weights)

        # Normalize
        weights = weights / weights.sum()

        # Covariance matrix
        cov_matrix = returns_df.cov()

        # Portfolio variance and volatility
        portfolio_var = weights @ cov_matrix @ weights
        portfolio_vol = np.sqrt(portfolio_var)

        # Marginal contribution to risk
        mcr = (cov_matrix @ weights) / portfolio_vol

        # Component contribution to risk
        ccr = weights * mcr

        # Risk contribution percentage
        rcr_pct = ccr / portfolio_vol

        results = {}
        for i, asset in enumerate(returns_df.columns):
            results[asset] = {
                'Weight': weights[i],
                'Marginal_Contribution': mcr[i],
                'Component_Contribution': ccr[i],
                'Risk_Contribution_Pct': rcr_pct[i] * 100
            }

        return {
            'Portfolio_Volatility': portfolio_vol,
            'Asset_Risk_Decomposition': results,
            'Sum_Component_Contributions': ccr.sum(),
            'Method': 'Risk Decomposition'
        }

    # ==================== UTILITY METHODS ====================

    @staticmethod
    def _estimate_df_from_kurtosis(kurtosis_value=None):
        """
        Estimate degrees of freedom for Student's t distribution from kurtosis

        For Student's t: kurtosis = 6/(df - 4) for df > 4
        Solving: df = 6/kurtosis + 4

        Mathematical Formula:
        K(df) = 6/(df - 4)
        df = 6/K + 4
        """
        if kurtosis_value is None:
            kurtosis_value = 3.0  # Normal distribution

        # Ensure positive df
        if kurtosis_value > 0:
            df = 6 / kurtosis_value + 4
            df = max(df, 2.1)  # Minimum degrees of freedom
        else:
            df = 30  # Default for near-normal

        return df

    def var_summary_report(self, portfolio_value=1.0, period=1):
        """
        Generate comprehensive VaR summary across multiple methods

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon

        Returns:
        --------
        pd.DataFrame : Summary comparison of all VaR methods
        """
        results = {
            'Historical': self.var_historical(portfolio_value, period)['VaR'],
            'Parametric_Normal': self.var_parametric_normal(portfolio_value, period)['VaR'],
            'Parametric_StudentT': self.var_parametric_student_t(portfolio_value, period)['VaR'],
            'Cornish_Fisher': self.var_parametric_cornish_fisher(portfolio_value, period)['VaR'],
            'Monte_Carlo': self.var_monte_carlo(portfolio_value, period)['VaR'],
            'Bootstrap': self.var_monte_carlo_historical_bootstrap(portfolio_value, period)['VaR']
        }

        return pd.DataFrame(list(results.items()), columns=['Method', 'VaR'])

    def risk_metrics_summary(self, portfolio_value=1.0, period=1):
        """
        Generate comprehensive risk metrics summary

        Parameters:
        -----------
        portfolio_value : float
            Portfolio value
        period : int
            Time horizon

        Returns:
        --------
        dict : Summary of all key risk metrics
        """
        var_hist = self.var_historical(portfolio_value, period)
        cvar_hist = self.cvar_historical(portfolio_value, period)
        var_param = self.var_parametric_normal(portfolio_value, period)
        cvar_param = self.cvar_parametric_normal(portfolio_value, period)

        return {
            'VaR_Historical': var_hist['VaR'],
            'CVaR_Historical': cvar_hist['CVaR'],
            'VaR_Parametric': var_param['VaR'],
            'CVaR_Parametric': cvar_param['CVaR'],
            'Mean_Return': self.mean_return * np.sqrt(252),
            'Annual_Volatility': self.std_return * np.sqrt(252),
            'Skewness': self.skewness,
            'Kurtosis': self.kurtosis,
            'Sharpe_Ratio': (self.mean_return * 252) / (self.std_return * np.sqrt(252)) if self.std_return > 0 else 0,
            'Confidence_Level': self.confidence_level,
            'Time_Horizon_Days': period
        }


# ==================== Utility Functions ====================

def compare_var_methods(returns_data, portfolio_value=1.0, confidence_level=0.95):
    """
    Compare all VaR methods on the same data

    Parameters:
    -----------
    returns_data : pd.Series
        Return series
    portfolio_value : float
        Portfolio value
    confidence_level : float
        Confidence level for VaR

    Returns:
    --------
    pd.DataFrame : Comparison of all VaR methods
    """
    risk_metrics = RiskMetrics(returns_data, confidence_level=confidence_level)

    comparison = risk_metrics.var_summary_report(portfolio_value=portfolio_value)

    return comparison


def calculate_portfolio_var(returns_dict, weights, confidence_level=0.95):
    """
    Calculate portfolio VaR given individual asset returns and weights

    Parameters:
    -----------
    returns_dict : dict
        Dictionary of asset names to return series
    weights : dict or np.array
        Portfolio weights
    confidence_level : float
        Confidence level

    Returns:
    --------
    dict : Portfolio-level risk metrics
    """
    returns_df = pd.DataFrame(returns_dict)

    # Get weights
    if isinstance(weights, dict):
        w = np.array([weights[asset] for asset in returns_df.columns])
    else:
        w = np.array(weights)

    w = w / w.sum()

    # Portfolio returns
    portfolio_returns = (returns_df * w).sum(axis=1)

    # Calculate risk metrics
    risk = RiskMetrics(portfolio_returns, confidence_level=confidence_level)

    return {
        'Portfolio_VaR_Historical': risk.var_historical()['VaR'],
        'Portfolio_CVaR_Historical': risk.cvar_historical()['CVaR'],
        'Portfolio_VaR_Parametric': risk.var_parametric_normal()['VaR'],
        'Portfolio_Annual_Vol': risk.std_return * np.sqrt(252),
        'Portfolio_Annual_Return': risk.mean_return * 252
    }


if __name__ == '__main__':
    # Example usage
    print("Risk Management Module - Import and use with your data")
    print("Example: risk = RiskMetrics(returns_data)")
    print("         var = risk.var_historical(portfolio_value=1000000)")
    print("         cvar = risk.cvar_historical(portfolio_value=1000000)")
    print("         summary = risk.risk_metrics_summary(portfolio_value=1000000)")
