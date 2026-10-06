#%%
"[markdown]"


# %%
import numpy as np
import matplotlib.pyplot as plt

r= np.linspace(0, 10, 100)
nr = 1.43**2*(1 - (r/20)**2)

plt.plot(r, nr)
plt.show()
print(np.sqrt(20))