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
blob:vscode-webview://094bkulee0k62n6ovc34v82n3g7d78hrcv9mnquqpmii7kcad6iv/fd6b827a-42ef-41a6-928f-415a475d7937
# %%
import sys
print(sys.executable)

# %%
