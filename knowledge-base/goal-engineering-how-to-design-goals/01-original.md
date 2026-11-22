# Goal Engineering: How to Design Goals

> 本文件仅保存正文原文及原文配图。中文梳理、公开资料补充和个人思考统一放在[观点梳理、思考总结](02-analysis.md)。

- **作者**：Harrison Chase
- **共同撰写**：[@mgarimella](https://x.com/mgarimella)（Actively AI）与 Anshul Gupta（Actively AI）
- **发布日期**：2026-11-15
- **原始文章**：https://x.com/hwchase17/article/2121635683999883577
- **原始帖子**：https://x.com/hwchase17/status/2121635683999883577
- **本地归档日期**：2026-11-15

## 标题索引

- [开篇：从任务执行走向开放目标](#goal-engineering-how-to-design-goals)
- [How to design goals](#how-to-design-goals)
- [Case Study: Actively AI](#case-study-actively-ai)
- [In the future](#in-the-future)

---

![Goal Engineering cover](assets/00-cover.webp)

*Written in conjunction with [@mgarimella](https://x.com/mgarimella) (Actively AI) and Anshul Gupta (Actively AI)*

The scope of tasks that agents can take on has increased drastically over the past few years. They have gone from simple text generation to tool calling and decision making to executing full tasks. The future of agents is them taking on open ended goals and driving towards completion of those goals. Launches like that of [Hone](https://x.com/hone/status/2108218574926176490?s=20) give us a glimpse into that future.

In this world, designing the scope of agents is crucial. Point them in the wrong direction, and you’ll get a lot of wasted tokens. A key part of the Hone agent set up is defining metrics for them to optimize.

![Goal Engineering](assets/01-open-ended-goals.jpg)

## How to design goals

As we’ve worked on similar styles of agents, we’ve realized something about designing the scope for agents: you want to design the scope of an agent such that it makes it as easy as possible to give feedback as the agent operates within that scope.

Why is this?

When agents mess up, a big reason they mess up is lack of right context. In order to fix this, you need to give the agent the right context. There are different types of context. Some types of context are things like access to the right documents or APIs - that is relatively easy to fix. The trickiest context to give the agent is context that is not written down anywhere already. This context needs to be given to the agent as feedback from a human expert.

This is especially important as agents expand beyond doing verifiable tasks and start taking on subjective work alongside humans within an organization. For example, if you want an agent to help optimize a business metric (like improving your ads to optimize marketing performance), there are so many nuances beyond just factual context that you want to govern how the agent behaves. You probably have a certain taste around what sounds and looks good. You have opinions about how provocative or out-there your brand can be. An agent that can’t effectively get feedback to learn these things quickly becomes useless.

![Written context and human feedback](assets/02-feedback-scope.jpg)

If the scope of your agent makes it really easy to give lots of high quality feedback on the agent’s work, that will help you immensely in building an agent that can reliably pursue a long-horizon goal.

A related learning is that you want to invest a lot in an intuitive and delightful UX for reviewing agent work. The bottleneck for agents performing is often them learning from feedback. Therefore, you should seek to optimize ease and quality of feedback collection! Investing in a clear UX for that is a worthwhile investment.

## Case Study: Actively AI

Let’s look at an example from [Actively AI](https://actively.ai/), which builds agents for sales teams.

Actively’s first goal-oriented agent experience was designed in a way where they had an agent per account (a prospective customer a sales team wants to sell to). The agent was tasked with the goal of moving the account forward and produced actions for sales reps to approve. Intuitively, this made sense - this was a relatively constrained and directed goal with a solid outcome. Naively, it seemed like the context about the account was the most important context for the agent to have, so you should orient an agent around that.

As the agents worked, they found that there was another source of important context the agent needed: how to do its job efficiently. Specifically, how to outbound, how to reply, how to strategize about deals, how aggressive to be, how to navigate a large org, etc. This type of context was spread across multiple agents - if you learn something about outbounding in one account, you very frequently want to transfer that learning to other accounts as well.

Actively found that when the agent was tackling a single account, it was tough for salespeople to efficiently use - and provide feedback to - the agent. There are many different jobs the agent has to do when progressing a single account, and those can often be spread out over time. They found that (a) there was a lot of context switching between agents (since there was only a few things that needed review at any point in time for a single agent) and (b) it was an awkward UX to share learnings across agents (which was needed, since they were learning the same thing).

The second version of Actively’s agent experience fixed this. Their new goal-oriented agents (built on [Deep Agents](https://github.com/langchain-ai/deepagents)!) are called “motions”. A motion is a particular job to be done - like outbounding or early-stage deal progression. How to do that job is not well defined and a lot of it even relates to an individual sales rep’s preferences. Lots of knowledge is in the seller's head that needs to be given as feedback to the agent in charge of that motion for it to learn. Since a motion is a bunch of similar tasks, it is pretty easy for a salesperson to review them all together. Any feedback learned from one task in a motion intuitively transfers to other tasks in the motion.

This aligns feedback (both scope of feedback, and ease of giving feedback) with the agents themselves, which makes it far easier to create powerful agents.

This isn’t to say that account context isn’t important - it obviously is! But that account context is often already written down and much more objective. So Actively has context-gathering agents that run in the background and assemble context on each account, but the actual work of progressing accounts down the funnel is now handled by motions that work across many accounts. They own the slice of a sales motion, learn much more quickly from feedback, and pull in each account’s context as needed.

![Actively's account and motion architectures](assets/03-actively-motions.jpg)

## In the future

In the future, agents will advance to the point where you just give them a goal, and they go out and work to optimize that goal.

Human review of work these agents are doing takes a lot of time - but it is so valuable. That is how you teach these agents what to do, and adapt them for your domain. This knowledge that is only in peoples heads is so important to extract in a form that is easy to pass to agents.

In order to best do this, you will want to align an agent’s goals to what is easiest for humans to review. This allows you to create a delightful review UX, extract the most information possible, and enable your agents to continually learn so they can be increasingly useful and autonomous over time.

Prompt engineering and context engineering will disappear, but goal engineering will remain.

---

## 原图来源

| 本地文件 | 原始素材 URL | 在原文中的位置 |
| --- | --- | --- |
| `00-cover.webp` | https://x.com/hwchase17/article/2121635683999883577/media/2121383046888976384 | 文章封面 |
| `01-open-ended-goals.jpg` | https://x.com/hwchase17/article/2121635683999883577/media/2121383145908170752 | 开篇之后 |
| `02-feedback-scope.jpg` | https://x.com/hwchase17/article/2121635683999883577/media/2121383307858649088 | How to design goals |
| `03-actively-motions.jpg` | https://x.com/hwchase17/article/2121635683999883577/media/2121383251852079104 | Case Study 之后 |

图片版权归原权利人所有，此处仅作项目内部学习和研究归档。
