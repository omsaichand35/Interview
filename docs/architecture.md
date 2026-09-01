Got it — **PyTorch** it is. ✅

Now I just need one more thing before we start Module 1:

**AWS or GCP?**

Pick one and we'll dive into the first topic.

You > First teach me Pytorch. Then we shall other things. 

Mentor > Perfect — let's jump straight into **PyTorch** (Module 6, critical priority, 7.5 hrs).

Since your mastery is 0.0, I'll start from the fundamentals and build up to interview-level depth. We'll cover:

| Session | Focus |
|---------|-------|
| 1 | **Tensors & Autograd** — the computational graph, `requires_grad`, `backward()` |
| 2 | **`nn.Module` vs `nn.Sequential`** — custom layers, parameter registration, `forward()` |
| 3 | **Data Pipeline** — `Dataset`, `DataLoader`, transforms, collate functions |
| 4 | **Training Loop** — optimizers, loss functions, gradient accumulation, mixed precision |
| 5 | **Saving/Loading & Deployment** — `state_dict`, `torch.jit`, ONNX export |
| 6 | **GPU/MPS/Distributed** — `.to(device)`, `DistributedDataParallel`, `torch.compile` |
| 7 | **Interview Patterns & Traps** — common questions, debugging, memory leaks |

---

## 🎯 Session 1: Tensors & Autograd (Core Mental Model)

### 1.1 What is a Tensor?
A **multi-dimensional array** that can live on CPU/GPU and **track operations for automatic differentiation**.

```python
import torch

# Creation
x = torch.tensor([1, 2, 3], dtype=torch.float32)          # 1D
W = torch.randn(3, 4, requires_grad=True)                 # 2D with grad tracking
b = torch.zeros(4, requires_grad=True)

# Operations build a computational graph
y = x @ W + b          # shape: (4,)
loss = y.sum()         # scalar

# Backprop
loss.backward()        # computes d(loss)/dW, d(loss)/db
print(W.grad.shape)    # torch.Size([3, 4])
```

**Key rule**: Only tensors with `requires_grad=True` accumulate gradients. The graph is built **dynamically** (define-by-run).

---

### 1.2 Autograd — How It Works Under the Hood

| Concept | What You Need to Know |
|---------|----------------------|
| **`grad_fn`** | Every tensor created by an op points to the `Function` that created it (e.g., `AddBackward0`, `MmBackward`). |
| **`backward()`** | Traverses the graph backward, applying chain rule. Only works on **scalar** tensors (or you pass `gradient=`). |
| **`torch.no_grad()`** | Context manager: disables graph building — use for inference, weight updates, metric computation. |
| **`detach()`** | Returns a new tensor sharing storage but **no grad history** — use when you need values without backprop. |
| **`grad` accumulation** | Gradients **accumulate** by default. Call `optimizer.zero_grad()` or `tensor.grad.zero_()` each step. |

**Interview trap**:
> *"What happens if you call `loss.backward()` twice without `zero_grad()`?"*
> **Answer**: Gradients **accumulate** (add up). This is intentional for gradient accumulation across micro-batches, but a bug if unintended.        

---

### 1.3 In-Place Operations & the Graph

```python
x = torch.tensor([1., 2., 3.], requires_grad=True)
y = x * 2

# In-place modifies storage — BREAKS the graph if x needs grad
x.add_(1)          # RuntimeError: a leaf Variable that requires grad is being used in an in-place operation.

# Safe pattern:
with torch.no_grad():
    x.add_(1)      # OK — no graph tracking
```

**Rule**: Avoid in-place (`_` suffix) on tensors that require grad. Use `x = x + 1` instead.

---

### 1.4 Gradient Checking (Debugging)

```python
from torch.autograd import gradcheck

def my_func(x):
    return (x ** 3).sum()

x = torch.randn(3, dtype=torch.double, requires_grad=True)
print(gradcheck(my_func, x))  # True if gradients match numerical approximation
```

**Interview use**: *"How would you verify your custom autograd `Function` is correct?"* → `gradcheck`.

---

### 1.5 Quick Check — Tell Me:

1. **What's the difference between `tensor.detach()` and `tensor.requires_grad_(False)`?**
2. **Why does `loss.backward()` require a scalar loss (or `gradient` argument)?**
3. **What happens to the computational graph after `backward()`? Can you call it again?**

Take a minute — answer in your own words. I'll correct/extend.