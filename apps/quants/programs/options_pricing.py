"""
Options Pricing Module
Comprehensive implementation of options pricing methods including:
- Black-Scholes pricing
- Greeks (Delta, Gamma, Theta, Vega, Rho)
- Implied Volatility solver
- Binomial tree pricing
- Monte Carlo pricing
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq, minimize_scalar
from typing import Union, Tuple, Dict
import warnings


class OptionsPricing:
    """
    Options pricing models and calculations
    """

    # Mathematical Constants
    RFR = 0.05  # Risk-free rate (default)

    @staticmethod
    def black_scholes(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        Black-Scholes Option Pricing Formula

        Mathematical Formula:
        C = S * N(d1) - K * e^(-rT) * N(d2)
        P = K * e^(-rT) * N(-d2) - S * N(-d1)

        Where:
        d1 = (ln(S/K) + (r + σ²/2)T) / (σ * √T)
        d2 = d1 - σ * √T
        N(x) = Cumulative standard normal distribution

        Parameters:
        -----------
        S : float
            Current stock price
        K : float
            Strike price
        T : float
            Time to maturity (in years)
        r : float
            Risk-free rate
        sigma : float
            Volatility (annualized)
        option_type : str
            'call' or 'put'

        Returns:
        --------
        float
            Option price
        """
        if T <= 0:
            if option_type == 'call':
                return max(S - K, 0)
            else:
                return max(K - S, 0)

        # Calculate d1 and d2
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        # Calculate option price
        if option_type == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return price

    @staticmethod
    def black_scholes_delta(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate Delta using Black-Scholes

        Mathematical Formula:
        Delta_call = N(d1)
        Delta_put = N(d1) - 1 = -N(-d1)

        Delta measures the rate of change of option price with respect to stock price

        Returns:
        --------
        float
            Delta value (0 to 1 for call, -1 to 0 for put)
        """
        if T <= 0:
            return 1.0 if option_type == 'call' and S > K else 0.0

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

        if option_type == 'call':
            delta = norm.cdf(d1)
        elif option_type == 'put':
            delta = norm.cdf(d1) - 1
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return delta

    @staticmethod
    def black_scholes_gamma(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float
    ) -> float:
        """
        Calculate Gamma using Black-Scholes

        Mathematical Formula:
        Gamma = N'(d1) / (S * σ * √T)

        Where N'(x) is the probability density function of standard normal

        Gamma measures the rate of change of delta with respect to stock price

        Returns:
        --------
        float
            Gamma value (always positive)
        """
        if T <= 0:
            return 0.0

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

        return gamma

    @staticmethod
    def black_scholes_vega(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float
    ) -> float:
        """
        Calculate Vega using Black-Scholes

        Mathematical Formula:
        Vega = S * N'(d1) * √T

        Vega measures the rate of change of option price with respect to volatility
        Note: Vega is the same for calls and puts

        Returns:
        --------
        float
            Vega value (per 1% change in volatility)
        """
        if T <= 0:
            return 0.0

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T)

        return vega / 100  # Per 1% change in volatility

    @staticmethod
    def black_scholes_theta(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate Theta using Black-Scholes

        Mathematical Formula:
        Theta_call = -(S * N'(d1) * σ) / (2 * √T) - r * K * e^(-rT) * N(d2)
        Theta_put = -(S * N'(d1) * σ) / (2 * √T) + r * K * e^(-rT) * N(-d2)

        Theta measures the rate of change of option price with respect to time
        (time decay, usually negative for long option positions)

        Returns:
        --------
        float
            Theta value (per day, usually annualized / 365)
        """
        if T <= 0:
            return 0.0

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        first_term = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))

        if option_type == 'call':
            theta = first_term - r * K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            theta = first_term + r * K * np.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return theta / 365  # Per day

    @staticmethod
    def black_scholes_rho(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate Rho using Black-Scholes

        Mathematical Formula:
        Rho_call = K * T * e^(-rT) * N(d2)
        Rho_put = -K * T * e^(-rT) * N(-d2)

        Rho measures the rate of change of option price with respect to interest rate

        Returns:
        --------
        float
            Rho value (per 1% change in interest rate)
        """
        if T <= 0:
            return 0.0

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return rho / 100  # Per 1% change in rate

    @staticmethod
    def calculate_greeks(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> Dict[str, float]:
        """
        Calculate all Greeks for an option

        Returns:
        --------
        Dict
            Dictionary with delta, gamma, theta, vega, rho
        """
        greeks = {
            'delta': OptionsPricing.black_scholes_delta(S, K, T, r, sigma, option_type),
            'gamma': OptionsPricing.black_scholes_gamma(S, K, T, r, sigma),
            'theta': OptionsPricing.black_scholes_theta(S, K, T, r, sigma, option_type),
            'vega': OptionsPricing.black_scholes_vega(S, K, T, r, sigma),
            'rho': OptionsPricing.black_scholes_rho(S, K, T, r, sigma, option_type)
        }
        return greeks

    @staticmethod
    def implied_volatility(
        option_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: str = 'call',
        initial_guess: float = 0.3,
        tolerance: float = 1e-6
    ) -> float:
        """
        Calculate Implied Volatility using Newton-Raphson method

        Mathematical Approach:
        Uses Vega (derivative of price with respect to volatility) for Newton-Raphson:
        σ_new = σ_old - (BS_Price(σ_old) - Market_Price) / Vega(σ_old)

        Parameters:
        -----------
        option_price : float
            Market price of the option
        S : float
            Current stock price
        K : float
            Strike price
        T : float
            Time to maturity
        r : float
            Risk-free rate
        option_type : str
            'call' or 'put'
        initial_guess : float
            Initial volatility estimate (default 0.3 = 30%)
        tolerance : float
            Convergence tolerance

        Returns:
        --------
        float
            Implied volatility
        """
        def objective(sigma):
            if sigma <= 0:
                return 1e10
            return abs(OptionsPricing.black_scholes(S, K, T, r, sigma, option_type) - option_price)

        try:
            # Use brentq for robust root finding
            def price_diff(sigma):
                if sigma <= 0:
                    return option_price + 1  # Ensure different from target
                return OptionsPricing.black_scholes(S, K, T, r, sigma, option_type) - option_price

            # Find bounds where sign changes
            if price_diff(0.001) * price_diff(10.0) > 0:
                # If no sign change, use minimize instead
                result = minimize_scalar(objective, bounds=(0.001, 10.0), method='bounded')
                return result.x
            else:
                return brentq(price_diff, 0.001, 10.0, xtol=tolerance)
        except ValueError:
            warnings.warn("Could not find implied volatility, returning initial guess")
            return initial_guess

    @staticmethod
    def binomial_tree(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        n_steps: int = 100,
        option_type: str = 'call'
    ) -> float:
        """
        Binomial Tree Option Pricing

        Mathematical Formula:
        Up factor: u = e^(σ√Δt)
        Down factor: d = 1/u
        Risk-neutral probability: p = (e^(rΔt) - d) / (u - d)

        Recursively: C(t) = e^(-rΔt) * [p * C_up(t+1) + (1-p) * C_down(t+1)]

        Parameters:
        -----------
        S : float
            Current stock price
        K : float
            Strike price
        T : float
            Time to maturity
        r : float
            Risk-free rate
        sigma : float
            Volatility
        n_steps : int
            Number of time steps in tree
        option_type : str
            'call' or 'put'

        Returns:
        --------
        float
            Option price
        """
        dt = T / n_steps
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(r * dt) - d) / (u - d)

        # Initialize stock prices at final nodes
        stock_prices = np.zeros(n_steps + 1)
        for i in range(n_steps + 1):
            stock_prices[i] = S * (u ** (n_steps - i)) * (d ** i)

        # Initialize option values at final nodes
        option_values = np.zeros(n_steps + 1)
        for i in range(n_steps + 1):
            if option_type == 'call':
                option_values[i] = max(stock_prices[i] - K, 0)
            elif option_type == 'put':
                option_values[i] = max(K - stock_prices[i], 0)
            else:
                raise ValueError("option_type must be 'call' or 'put'")

        # Backward induction through the tree
        for j in range(n_steps - 1, -1, -1):
            for i in range(j + 1):
                stock_prices[i] = S * (u ** (j - i)) * (d ** i)
                option_values[i] = (np.exp(-r * dt) *
                                   (p * option_values[i] + (1 - p) * option_values[i + 1]))

        return option_values[0]

    @staticmethod
    def monte_carlo(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        n_simulations: int = 10000,
        n_steps: int = 252,
        option_type: str = 'call',
        random_seed: int = None
    ) -> Tuple[float, float]:
        """
        Monte Carlo Option Pricing

        Mathematical Formula:
        Geometric Brownian Motion: dS = μ*S*dt + σ*S*dW
        Discretized: S(t+Δt) = S(t) * exp((r - σ²/2)Δt + σ*√Δt*Z)

        Where Z ~ N(0,1) (standard normal random variable)

        Price = e^(-rT) * E[max(S(T) - K, 0)] for call

        Parameters:
        -----------
        S : float
            Current stock price
        K : float
            Strike price
        T : float
            Time to maturity
        r : float
            Risk-free rate
        sigma : float
            Volatility
        n_simulations : int
            Number of Monte Carlo simulations
        n_steps : int
            Number of steps per simulation (default 252 = trading days per year)
        option_type : str
            'call' or 'put'
        random_seed : int
            Random seed for reproducibility

        Returns:
        --------
        Tuple[float, float]
            (Option price, Standard error)
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        dt = T / n_steps
        sqrt_dt = np.sqrt(dt)

        # Generate random paths
        # Shape: (n_simulations, n_steps)
        Z = np.random.standard_normal((n_simulations, n_steps))

        # Initialize stock prices
        stock_paths = np.zeros((n_simulations, n_steps + 1))
        stock_paths[:, 0] = S

        # Simulate paths using geometric Brownian motion
        for t in range(1, n_steps + 1):
            stock_paths[:, t] = (stock_paths[:, t - 1] *
                               np.exp((r - 0.5 * sigma ** 2) * dt +
                                     sigma * sqrt_dt * Z[:, t - 1]))

        # Calculate option payoff at maturity
        final_prices = stock_paths[:, -1]

        if option_type == 'call':
            payoffs = np.maximum(final_prices - K, 0)
        elif option_type == 'put':
            payoffs = np.maximum(K - final_prices, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        # Discount and average
        option_price = np.exp(-r * T) * np.mean(payoffs)
        std_error = np.std(payoffs) / np.sqrt(n_simulations)

        return option_price, std_error

    @staticmethod
    def american_binomial(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        n_steps: int = 100,
        option_type: str = 'put'
    ) -> float:
        """
        American Option Pricing using Binomial Tree
        (with early exercise capability)

        Modification to binomial tree:
        At each node: Option_Value = max(Intrinsic_Value, Discounted_Expected_Value)

        Parameters:
        -----------
        S : float
            Current stock price
        K : float
            Strike price
        T : float
            Time to maturity
        r : float
            Risk-free rate
        sigma : float
            Volatility
        n_steps : int
            Number of time steps
        option_type : str
            'call' or 'put'

        Returns:
        --------
        float
            American option price
        """
        dt = T / n_steps
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(r * dt) - d) / (u - d)

        # Initialize option values at final nodes
        option_values = np.zeros(n_steps + 1)
        for i in range(n_steps + 1):
            stock_price = S * (u ** (n_steps - i)) * (d ** i)
            if option_type == 'call':
                option_values[i] = max(stock_price - K, 0)
            elif option_type == 'put':
                option_values[i] = max(K - stock_price, 0)

        # Backward induction with early exercise
        for j in range(n_steps - 1, -1, -1):
            for i in range(j + 1):
                stock_price = S * (u ** (j - i)) * (d ** i)

                # Discounted expected value
                continuation_value = (np.exp(-r * dt) *
                                     (p * option_values[i] + (1 - p) * option_values[i + 1]))

                # Intrinsic value
                if option_type == 'call':
                    intrinsic_value = max(stock_price - K, 0)
                elif option_type == 'put':
                    intrinsic_value = max(K - stock_price, 0)

                # Take maximum (early exercise if beneficial)
                option_values[i] = max(intrinsic_value, continuation_value)

        return option_values[0]


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("OPTIONS PRICING DEMONSTRATION")
    print("=" * 60)

    # Parameters
    S = 100      # Stock price
    K = 100      # Strike price
    T = 1.0      # 1 year to maturity
    r = 0.05     # 5% risk-free rate
    sigma = 0.2  # 20% volatility

    print(f"\nParameters:")
    print(f"Stock Price (S): ${S}")
    print(f"Strike Price (K): ${K}")
    print(f"Time to Maturity (T): {T} year")
    print(f"Risk-free Rate (r): {r*100}%")
    print(f"Volatility (σ): {sigma*100}%")

    # Black-Scholes Call Option
    call_price = OptionsPricing.black_scholes(S, K, T, r, sigma, 'call')
    print(f"\n--- BLACK-SCHOLES PRICING ---")
    print(f"Call Option Price: ${call_price:.4f}")

    put_price = OptionsPricing.black_scholes(S, K, T, r, sigma, 'put')
    print(f"Put Option Price: ${put_price:.4f}")

    # Greeks for Call
    greeks = OptionsPricing.calculate_greeks(S, K, T, r, sigma, 'call')
    print(f"\n--- GREEKS (CALL OPTION) ---")
    print(f"Delta: {greeks['delta']:.4f}")
    print(f"Gamma: {greeks['gamma']:.6f}")
    print(f"Theta: {greeks['theta']:.6f}")
    print(f"Vega: {greeks['vega']:.6f}")
    print(f"Rho: {greeks['rho']:.6f}")

    # Implied Volatility
    iv = OptionsPricing.implied_volatility(call_price, S, K, T, r, 'call')
    print(f"\n--- IMPLIED VOLATILITY ---")
    print(f"Implied Volatility (from BS call): {iv:.4f} ({iv*100:.2f}%)")

    # Binomial Tree
    binomial_call = OptionsPricing.binomial_tree(S, K, T, r, sigma, n_steps=100, option_type='call')
    print(f"\n--- BINOMIAL TREE PRICING (100 steps) ---")
    print(f"Call Option Price: ${binomial_call:.4f}")

    binomial_put = OptionsPricing.binomial_tree(S, K, T, r, sigma, n_steps=100, option_type='put')
    print(f"Put Option Price: ${binomial_put:.4f}")

    # Monte Carlo
    mc_call, mc_std_err = OptionsPricing.monte_carlo(
        S, K, T, r, sigma, n_simulations=10000, n_steps=252, option_type='call'
    )
    print(f"\n--- MONTE CARLO PRICING (10,000 simulations) ---")
    print(f"Call Option Price: ${mc_call:.4f}")
    print(f"Standard Error: ${mc_std_err:.6f}")

    # American Put
    american_put = OptionsPricing.american_binomial(S, K, T, r, sigma, n_steps=100, option_type='put')
    print(f"\n--- AMERICAN OPTION PRICING ---")
    print(f"American Put Price: ${american_put:.4f}")
    print(f"European Put Price: ${put_price:.4f}")
    print(f"Early Exercise Premium: ${american_put - put_price:.4f}")

    # Comparison
    print(f"\n--- PRICING COMPARISON (Call) ---")
    print(f"Black-Scholes: ${call_price:.4f}")
    print(f"Binomial Tree: ${binomial_call:.4f}")
    print(f"Monte Carlo: ${mc_call:.4f}")
    print(f"Binomial vs BS Difference: ${abs(binomial_call - call_price):.6f}")
    print(f"MC vs BS Difference: ${abs(mc_call - call_price):.6f}")
    print("=" * 60)
