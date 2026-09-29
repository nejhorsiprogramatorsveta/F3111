#%%
"[markdown]"


# %%
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10,10,1000)
X,Y = np.meshgrid(x,x)

mask = ((X**2 + Y**2) < 0.2).astype(int)
# mask = (np.abs(X)<0.2).astype(int)

plt.imshow(mask, extent=[-10,10,-10,10], origin='lower')
plt.colorbar()
plt.show()
#%%

ft = np.fft.fftshift(np.fft.fft2(mask))
kx = np.fft.fftshift(np.fft.fftfreq(mask.shape[0], d=(x[1]-x[0])))

plt.imshow(np.abs(ft)**2, extent=[kx[0], kx[-1], kx[0], kx[-1]], origin='lower')
plt.show()