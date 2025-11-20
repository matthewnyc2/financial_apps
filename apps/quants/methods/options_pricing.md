# Options Pricing Methods

## Overview
This document provides comprehensive coverage of options pricing methodologies, including the Black-Scholes model, Greeks calculations, binomial trees, and Monte Carlo simulation.

---

## 1. Black-Scholes Option Pricing Model

### History and Significance
The Black-Scholes model, developed by Fischer Black, Myron Scholes, and Robert Merton in 1973, revolutionized options pricing. Merton and Scholes won the 1997 Nobel Prize in Economics for this work.

### Assumptions
1. European-style options (exercise only at maturity)
2. No arbitrage opportunities
3. Stock follows geometric Brownian motion
4. No transaction costs or taxes
5. Constant risk-free rate and volatility
6. Log-normal distribution of stock prices
7. No dividends during option life

### Mathematical Formulation

#### Call Option Price
```
C = S₀ * N(d₁) - K * e^(-rT) * N(d₂)
```

#### Put Option Price
```
P = K * e^(-rT) * N(-d₂) - S₀ * N(-d₁)
```

#### Where:
```
d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
```

#### Variables:
- **S₀**: Current stock price
- **K**: Strike price
- **T**: Time to maturity (in years)
- **r**: Risk-free interest rate (annualized)
- **σ**: Volatility of stock returns (annualized)
- **N(x)**: Cumulative standard normal distribution function
- **e**: Mathematical constant (≈ 2.71828)
- **ln**: Natural logarithm

### Put-Call Parity
```
C - P = S₀ - K * e^(-rT)
```
This fundamental relationship must hold to prevent arbitrage.

---

## 2. The Greeks

The Greeks are sensitivity measures that quantify the risk of an option position.

### 2.1 Delta (Δ)

**Definition**: Rate of change of option price with respect to stock price

#### Call Delta:
```
Δ_call = N(d₁)
Range: 0 to 1
```

#### Put Delta:
```
Δ_put = N(d₁) - 1 = -N(-d₁)
Range: -1 to 0
```

**Interpretation**:
- Delta of 0.6 means: $1 increase in stock price → $0.60 increase in call price
- Used for hedging: "Delta-neutral" portfolio requires matching long stock with short calls

**Properties**:
- At-the-money (ATM): Δ ≈ 0.5 (call)
- Deep in-the-money: Δ ≈ 1.0 (call)
- Deep out-of-the-money: Δ ≈ 0 (call)
- Put delta always negative

### 2.2 Gamma (Γ)

**Definition**: Rate of change of delta with respect to stock price (second derivative)

#### Formula:
```
Γ = N'(d₁) / (S₀ * σ * √T)

Where N'(x) = (1/√(2π)) * e^(-x²/2) is the standard normal PDF
```

**Key Characteristics**:
- Always positive (for both calls and puts)
- Measures convexity of option price curve
- Highest for ATM options with short time to expiration
- Hedging: Gamma neutrality requires adjustment as delta changes

**Practical Meaning**:
- Gamma of 0.05: Delta changes by 0.05 for $1 move in stock price
- High gamma = high risk (delta changes rapidly)
- Useful for dynamic hedging strategies

### 2.3 Theta (Θ)

**Definition**: Rate of change of option price with respect to time (time decay)

#### Call Theta:
```
Θ_call = -[S₀ * N'(d₁) * σ] / (2√T) - r * K * e^(-rT) * N(d₂)
```

#### Put Theta:
```
Θ_put = -[S₀ * N'(d₁) * σ] / (2√T) + r * K * e^(-rT) * N(-d₂)
```

**Key Characteristics**:
- Usually negative for long options (time decay works against holder)
- Usually positive for short options (time decay benefits seller)
- Accelerates as expiration approaches
- Highest for ATM options
- Per calendar day: Divide by 365

**Practical Meaning**:
- Theta of -0.05: Option loses $0.05 per day (assuming other factors constant)
- Used in options trading for "theta decay" strategies
- Options sellers ("time sellers") profit from positive theta

### 2.4 Vega (ν)

**Definition**: Rate of change of option price with respect to volatility

#### Formula:
```
ν = S₀ * N'(d₁) * √T
```

**Key Characteristics**:
- Same for calls and puts
- Always positive
- Measures volatility sensitivity
- Per 1% change in volatility (basis point)
- Highest for ATM options with longer time to expiration

**Practical Meaning**:
- Vega of 0.20: 1% increase in volatility → $0.20 increase in option price
- Long volatility: Buy options (benefit from volatility increase)
- Short volatility: Sell options (profit from volatility decrease)
- Used in volatility trading strategies

### 2.5 Rho (ρ)

**Definition**: Rate of change of option price with respect to interest rate

#### Call Rho:
```
ρ_call = K * T * e^(-rT) * N(d₂)
```

#### Put Rho:
```
ρ_put = -K * T * e^(-rT) * N(-d₂)
```

**Key Characteristics**:
- Per 1% change in interest rate (basis point)
- More significant for longer-dated options
- Less important than delta, gamma, theta for short-term trading
- Call options benefit from rising rates, puts suffer

**Practical Meaning**:
- Rho of 0.10: 1% rise in interest rates → $0.10 increase in call price
- Important for bond options and currency options
- Less relevant for equity options with short maturity

---

## 3. Implied Volatility

### Definition
The volatility level that makes the theoretical option price equal to the market price.

### Importance
- Market's expectation of future volatility
- Not directly observable (unlike historical volatility)
- Traders monitor changes in IV ("IV crush," "IV expansion")
- Critical for options trading strategies

### Calculation Methods

#### Newton-Raphson Method (Fastest)
```
σ_new = σ_old - (BS_Price(σ_old) - Market_Price) / Vega(σ_old)
```
Converges quickly using Vega as derivative.

#### Bisection Method (Robust)
- Slower but guaranteed convergence
- Used as fallback when Newton-Raphson fails

#### Properties
- No closed-form solution (must use numerical methods)
- One IV for each option price
- Uniqueness guaranteed within reasonable bounds
- Used for "volatility surface" (IV varies by strike and expiration)

### Volatility Smile and Skew
- **Smile**: IV higher for OTM and ITM options, lower for ATM
- **Skew**: IV higher on one side (common in equity markets)
- **Term Structure**: Different volatilities for different expirations
- These violate Black-Scholes assumption of constant volatility

---

## 4. Binomial Tree Pricing

### History
Developed by Cox, Ross, and Rubinstein (1979) as discrete-time alternative to Black-Scholes.

### Advantages
- Handles American options (with early exercise)
- Intuitive and easy to understand
- Flexible for various scenarios
- Works with discrete dividends

### Model Structure

#### Time Step Discretization
- Divide time [0, T] into n steps of Δt = T/n

#### Up and Down Factors
```
u = e^(σ√Δt)
d = 1/u = e^(-σ√Δt)
```

#### Risk-Neutral Probability
```
p = (e^(rΔt) - d) / (u - d)
```
This ensures expected value of stock equals forward price.

#### Stock Price Lattice
At time step j and state i:
```
S(j,i) = S₀ * u^(j-i) * d^i
```

### Pricing Algorithm

1. **Initialize terminal nodes**: Calculate intrinsic values at maturity
2. **Backward induction**: At each node, calculate:
   ```
   C(j,i) = e^(-rΔt) * [p * C(j+1,i) + (1-p) * C(j+1,i+1)]
   ```
3. **Return root value**: C(0,0) is the option price

### European vs American Options

#### European (Black-Scholes formula):
```
Option_Value = Discounted_Expected_Value
```

#### American (with early exercise):
```
Option_Value = max(Intrinsic_Value, Discounted_Expected_Value)
```

### Convergence
- As n → ∞, binomial price → Black-Scholes price
- Typical: 50-100 steps sufficient for accuracy
- 1000+ steps for production trading systems

---

## 5. Monte Carlo Simulation

### Concept
Generate multiple random price paths and calculate option payoff for each, then average.

### Advantages
- Handles complex payoffs and path dependencies
- American options with Monte Carlo require Longstaff-Schwartz algorithm
- Flexible for exotic options
- Can incorporate term structure and other features

### Disadvantages
- Computationally intensive
- Standard error decreases as √(n_simulations)
- Not efficient for simple European options

### Stochastic Differential Equation (SDE)

#### Geometric Brownian Motion (GBM):
```
dS = μS dt + σS dW
```

Where:
- **μ**: Drift (expected return)
- **σ**: Volatility
- **dW**: Brownian motion increment
- **dt**: Time increment

#### Risk-Neutral Drift:
Under risk-neutral measure:
```
dS = rS dt + σS dW
```

### Discretization (Euler Scheme)

```
S(t+Δt) = S(t) * exp[(r - σ²/2)Δt + σ√Δt * Z]
```

Where Z ~ N(0,1) is a standard normal random variable.

### Algorithm

1. **Initialize**: S(0) = S₀
2. **Generate random paths**: For each simulation:
   - For each time step: Generate Z ~ N(0,1)
   - Update: S(t) using discretization formula
   - Store: S(T) at maturity
3. **Calculate payoffs**:
   - Call: max(S(T) - K, 0)
   - Put: max(K - S(T), 0)
4. **Discount and average**:
   ```
   Option_Price = e^(-rT) * (1/n) * Σ Payoff(i)
   Standard_Error = σ_payoff / √n
   ```

### Variance Reduction Techniques

#### Antithetic Variates
- If Z generates a path, use -Z for opposite path
- Reduces variance by exploiting symmetry
- Typical variance reduction: 30-50%

#### Control Variates
- Use Black-Scholes price as control
- Exploit correlation with Monte Carlo estimate
- Can achieve 90%+ variance reduction

#### Importance Sampling
- Generate paths more likely to be in-the-money
- Weight by probability ratio
- Efficient for deep OTM options

### Convergence
- Standard error ∝ 1/√n
- To reduce error by 10×, need 100× more simulations
- Rule of thumb: 10,000 simulations for 3 decimal place accuracy

---

## 6. American Options

### Characteristics
- Can be exercised at any time before expiration
- More valuable than European options
- Early exercise premium = American Price - European Price

### When to Exercise Early

#### American Call
- Rarely optimal before expiration (for non-dividend stocks)
- Exception: Just before large dividend, exercise might be optimal

#### American Put
- Often optimal to exercise when deep in-the-money
- Exercise premium can be substantial (5-20%)
- More significant as expiration approaches

### Pricing Methods

#### Binomial Tree (Best)
- Straightforward: Compare intrinsic vs continuation value
- O(n²) complexity

#### Longstaff-Schwartz Monte Carlo
- Regression-based approach
- Estimates continuation value at each node
- Practical for high-dimensional problems

#### Trinomial Tree
- More accurate than binomial
- Slower computation

---

## 7. Greeks Relationships

### Partial Derivatives Summary
```
Δ = ∂C/∂S (Delta)
Γ = ∂Δ/∂S = ∂²C/∂S² (Gamma)
Θ = -∂C/∂T (Theta)
ν = ∂C/∂σ (Vega)
ρ = ∂C/∂r (Rho)
```

### Gamma-Theta Relationship
```
Θ ≈ -0.5 * Γ * S² * σ²
```
For ATM options: Theta loss roughly offset by gamma profit if stock moves by σ*√dt.

### Put-Call Parity Implications
```
Δ_call - Δ_put = 1
Γ_call = Γ_put (same value)
Θ_call ≠ Θ_put (different time decay)
ν_call = ν_put (same volatility sensitivity)
ρ_call ≠ ρ_put (different interest rate sensitivity)
```

---

## 8. Comparison of Methods

| Method | European | American | Speed | Accuracy | Complexity |
|--------|----------|----------|-------|----------|-----------|
| Black-Scholes | ✓ | ✗ | Very Fast | Analytical | Low |
| Binomial | ✓ | ✓ | Fast | O(n²) | Medium |
| Trinomial | ✓ | ✓ | Medium | Better | Medium |
| Monte Carlo | ✓ | ✓* | Slow | O(n^-0.5) | High |
| Finite Difference | ✓ | ✓ | Medium | O(n³) | High |

*American MC requires Longstaff-Schwartz or least-squares method

---

## 9. Parameter Guidance

### Stock Price (S)
- Current market price
- Most sensitive input to delta

### Strike Price (K)
- Agreed exercise price
- In/At/Out of money affects all Greeks

### Time to Maturity (T)
- Years (0.01 = 3.65 days)
- Typically 0.001 to 30 years
- T → 0: Option → intrinsic value

### Risk-Free Rate (r)
- Typically 2-5% annually
- Use government bond yield matching maturity
- Affects discount factor and Rho

### Volatility (σ)
- Most uncertain parameter
- Annualized standard deviation of log returns
- Typical range: 5% to 100%+
- Estimated from: Historical data, implied volatility, or GARCH models

### Number of Steps (binomial)
- 50-100 adequate for most applications
- Increase to 500+ for production systems
- Convergence: O(1/n²)

### Simulations (Monte Carlo)
- 1,000 for quick estimates
- 10,000 for trading decisions
- 100,000+ for risk reports

---

## 10. Practical Considerations

### Black-Scholes Limitations
1. Assumes constant volatility (violated in practice)
2. Ignores transaction costs and taxes
3. European style only
4. Assumes log-normal distribution (tails heavier in reality)

### Volatility Calibration
- Use GARCH, EWMA, or realized volatility
- Adjust for mean reversion
- Consider term structure
- Account for volatility clustering

### Model Risk
- All models are approximations
- Validate against market prices
- Monitor Greeks in real trading
- Stress test assumptions

### Implementation Tips
- Use double precision floating point
- Check for division by zero (T → 0)
- Validate IV convergence (may not exist)
- Handle boundary cases gracefully
- Consider numerical stability in log-normal calculations

---

## 11. Further Resources

### Classic References
- Black, F., & Scholes, M. (1973). "The pricing of options and corporate liabilities"
- Cox, J. C., Ross, S. A., & Rubinstein, M. (1979). "Option pricing: A simplified approach"
- Longstaff, F. A., & Schwartz, E. S. (2001). "Valuing American options by simulation"
- Wilmott, P. (2006). "Paul Wilmott on Quantitative Finance" (2nd edition)

### Implementation Libraries
- QuantLib (C++): Full-featured derivatives library
- NumPy/SciPy (Python): Numerical computing
- Cython: Performance optimization for Python
- CUDA: GPU-accelerated Monte Carlo

### Advanced Topics
- Stochastic Volatility (Heston model)
- Jump Diffusion (Merton model)
- Interest Rate Models (Vasicek, Hull-White)
- Exotic Options (Asian, Barrier, Lookback)
- CVA and XVA adjustments

---

## Glossary

- **ATM (At-the-Money)**: Strike price equals current stock price
- **ITM (In-the-Money)**: Call: S > K; Put: K > S (has intrinsic value)
- **OTM (Out-of-the-Money)**: Call: S < K; Put: K < S (no intrinsic value)
- **Intrinsic Value**: Immediate exercise value = max(S-K, 0) for call
- **Time Value**: Option Price - Intrinsic Value
- **Volatility Smile**: IV higher for OTM/ITM than ATM
- **Volatility Skew**: IV higher on one side (typically puts)
- **Greeks**: Sensitivity measures (Delta, Gamma, Theta, Vega, Rho)
- **Vega Bleed**: Theta/Vega tradeoff for option sellers
- **Greeks Hedging**: Construct positions to neutralize Greeks

---

*Last Updated: November 2025*
*This documentation complements the options_pricing.py implementation*
