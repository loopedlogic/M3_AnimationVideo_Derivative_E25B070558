# Viva practice

**Why are P and Q distinct?** The secant slope requires two points. Here their horizontal separation is the signed number h. At h = 0 the two points coincide and the original ratio is 0/0.

**How is the slope derived?** For h ≠ 0, subtract 4 from (2 + h)² to get 4h + h². Divide by h to get 4 + h. This expression tends to 4 as h approaches zero from either side.

| h | Run | Rise | Secant slope |
|---:|---:|---:|---:|
| 1 | 1 | 5 | 5 |
| 0.1 | 0.1 | 0.41 | 4.1 |
| −0.1 | −0.1 | −0.39 | 3.9 |
| −0.01 | −0.01 | −0.0399 | 3.99 |
| 0.01 | 0.01 | 0.0401 | 4.01 |

**What is the tangent equation?** The slope is 4 and the line passes through (2, 4). Point-slope form gives y − 4 = 4(x − 2), which simplifies to y = 4x − 4. Substitution gives y = 4 at x = 2.

**Why does halving a small step quarter the gap?** At x = 2 + h, the curve gives 4 + 4h + h² and the tangent gives 4 + 4h. Their difference is h². Replacing h by h/2 gives h²/4.

**What does the code animate?** The graph maps math coordinates to pixel positions. Each animation frame updates h, computes Q = (2 + h, (2 + h)²), and redraws the secant through P with slope 4 + h. The rise and run are drawn as the two legs of a right triangle. Algebra panels reveal successive lines, and the final graph draws the tangent with slope 4.
