# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# %%
def model(t, y):
    return -0.1 * y

sol = solve_ivp(model, [0, 50], [100], dense_output=True)
t = np.linspace(0, 50, 200)

plt.plot(t, sol.sol(t)[0])
plt.xlabel('Time')
plt.ylabel('Concentration')
plt.show()
# %%
# %%
import sys
print(sys.executable)
# %%
