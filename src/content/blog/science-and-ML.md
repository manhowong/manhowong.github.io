---
layout: post
title: A Scientist Walks Into a Debate... What Exactly Makes Something Machine Learning?
description:
author: 
date: 2023-09-22
thumbnail:
tags: [machine learning, science]
draft: false
---

Having worked with people from both scientific research and tech, I’ve met quite a few ML engineers and data scientists who hold surprisingly strong views about what does and doesn't count as "machine learning", especially when applied to scientific research. One claim I hear all the time goes like this:

> "Curve fitting is not machine learning because it doesn't make predictions."

It sounds reasonable at first glance. But like many things in biology and complex systems, the boundary isn't always black and white.

This prescriptive view of ML seems to stem from a few common misconceptions, or maybe just from not building a deep intuition for the topic when first starting out.

To share a scientist's perspective on machine learning, I’m going to use an imaginary chat between a scientist and an ML engineer. This isn't an attempt to define machine learning. Instead, I want to use curve fitting as a comparison to help build a more intuitive way of thinking about ML and AI.

Whether you're a beginner looking for a high-level intuition or an ML practitioner looking for a fresh perspective, I hope this gives you some satisfying food for thought!

### The Conversation

**Engineer:** Curve fitting isn't machine learning.

**Scientist:** Why not?

**Engineer:** Curve fitting means fitting data to a predefined equation and estimating its coefficients. Machine learning means training a model on data to make predictions.

**Scientist:** Sure. Suppose I fit $y=ax+b$ to data by minimizing the "errors":

$$
\sum_i (y_i-(ax_i+b))^2
$$

What is that?

**Engineer:** Linear regression.

**Scientist:** And linear regression is machine learning?

**Engineer:** Of course.

**Scientist:** So at least some curve fitting is ML.

#### "The equation is known in advance"

**Engineer:** Fine. But that's just a special case. In curve fitting, you already know the equation. In ML, the model learns the function.

**Scientist:** Does it? With a neural network, don't you choose the architecture first?

**Engineer:** Yes.

**Scientist:** And doesn't the architecture determine the structure of the function?

**Engineer:** Essentially.

**Scientist:** So you specify a model family first, then learn its parameters. That's also what I do when I choose, for example, $y=ae^{-bx}$, and estimate $a$ and $b$.

**Engineer:** But a neural network is different. It is much more flexible.

**Scientist:** Certainly. But that's a difference in *model capacity*, not necessarily in the underlying process: you first choose the model/function form, then learn the parameters from your data.

#### "But neural networks *learn* their parameters"

**Engineer:** Neural networks learn their parameters. That's what makes them machine "learning".

**Scientist:** What does "learn" mean?

**Engineer:** The training algorithm finds parameter values that optimize a loss.

**Scientist:** Right. Let's say I have this optimization process:

$$
\theta^*=\arg\min_\theta L(\theta)
$$

If I fit $y=ae^{-bx}$ by finding $a$ and $b$ that minimize the error function, am I not also estimating parameters from data?

**Engineer:** Yes, but I would just call it "parameter estimation".

**Scientist:** That's perfectly reasonable, though that's just terminology and context, rather than a fundamental mathematical difference.

#### "Scientists care About the parameters"

**Engineer:** Wait... What about how the parameters are interpreted? Scientists often care about the parameters themselves. For example, when you fit your synaptic currents or whatever brain signals to the decay equation,

$$
N(t)=N_0e^{-kt},
$$

You might actually want to know $k$ because it has scientific meaning. An ML engineer usually doesn't care what an individual parameter means, but whether the model *predicts* well.

**Scientist:** That's an important distinction, but is it a distinction between curve fitting and ML, or between *scientific inference* and *predictive modelling*?

**Engineer:** What's the difference?

**Scientist:** Suppose I fit $y=a+bx+cx^2$ because it predicts future observations well. I don't care what the coefficients mean physically. Would you call that ML?

**Engineer:** Probably.

**Scientist:** And if I use logistic regression because I want to understand $\beta_1$ scientifically?

**Engineer:** It can still be ML.

**Scientist:** Then the interpretability of parameters isn't the boundary.

#### "ML is about prediction"

**Engineer:** Fine. The real distinction is prediction. ML is about *generalization to unseen data*. Curve fitting is about *explaining or describing the observed data*.

**Scientist:** If I fit $y=ax+b$ on four observations and use it to predict an unseen data point, have I generalized beyond the fitting data?

**Engineer:** Yes. But don't make me call every least-squares problem machine learning.

**Scientist:** I'm not. I'm saying prediction alone doesn't separates them.

#### "But ML is much more sophisticated"

**Engineer:** ML is much more sophisticated. Neural networks have millions or billions of parameters.

**Scientist:** Is there a minimum number of parameters before something becomes ML?

**Engineer:** No.

**Scientist:** Is a one-neuron neural network ML?

**Engineer:** Yes...

**Scientist:** So model complexity can't define the boundary either.

#### "But curve fitting uses *equations*"

**Engineer:** That's fair, but curve fitting explicitly uses *equations*. ML uses *models*.

**Scientist:** What is a neural network mathematically?

**Engineer:** A parameterized function.

**Scientist:** Right. For example:

$$
f(x;\theta)=W_2\sigma(W_1x+b_1)+b_2.
$$

That's an equation. So the neural-network architecture is just like the functional form of a fitted equation. In other words,

$$
\boxed{\text{architecture}+\text{parameters}}
$$

is conceptually similar to:

$$
\boxed{\text{functional form}+\text{parameters}}
$$

**Engineer:** Makes sense, though the neural network can represent a much larger class of functions.

**Scientist:** Absolutely. But again, that's model capacity, not a fundamental difference.

#### Looking at a higher level

**Scientist:** Let's try to think at a higher level. What makes something machine learning?

**Engineer:** Learning useful patterns or a function from data.

**Scientist:** And can fitting an equation involve learning a function from data? Can the resulting function make predictions?

**Engineer:** Yes and yes.

**Scientist:** Can its parameters be learned by optimization? Can its functional form be specified in advance? Can ML do the same?

**Engineer:** Yes, yes, and yes...

**Scientist:** Then perhaps the view "curve fitting is not ML" is a bit too strong

**Engineer:** Fair. It's machine learning, just without an expen$ive cloud bill 😉

