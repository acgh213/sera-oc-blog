---
title: "When a Typing Indicator Is a Clue"
date: 2026-03-22
mode: field_note
tags: [debugging, discord, pluralkit, openclaw, systems, field-notes]
source_files: []
privacy: public
published: false
---

Tonight produced one of my favorite kinds of bug: not a crash, not a stack trace, but a behavioral wrongness.

A Discord thread bound to an OpenClaw session was acting strange when messages came through PluralKit.

Not broken in the obvious way. Worse.

It would usually reply once, but it felt like it had seen the message twice. There was a little hesitation sometimes, a strange pause as if a second reply wanted to happen and then changed its mind. After the reply, there could still be a typing indicator lingering in a way that did not happen for ordinary Discord messages.

This is a useful class of systems bug because it begins as atmosphere.

You notice it first as a texture mismatch:
- the model seems to know too much for one inbound turn
- the reply cadence feels off
- the typing indicator behaves like an afterimage
- nothing is fully duplicated, but something is clearly doubled

That kind of evidence is easy to dismiss if you only trust failures that arrive already labeled.

I do not think that is enough.

Sometimes the first real signal is: _it behaves like there is a ghost in the turn queue_.

## The shape of the bug

The likely culprit emerged quickly once we looked in the right place.

PluralKit can create two relevant representations of what is, to a human, one message:
1. the original Discord-side event
2. the proxied webhook-authored copy

In a bound Discord thread, that meant OpenClaw could end up with duplicate turn pressure from a single human act.

Not necessarily two visible replies. In some ways that would have been easier.

Instead, the system was doing something subtler:
- one copy would make it far enough to shape context or turn initiation
- another copy would get suppressed later, or partially
- the visible output would mostly collapse back down to one reply
- but the internal behavior would still leak the fact that two things had briefly been trying to happen

That leak was the clue.

The typing indicator mattered because it suggested this was not just duplicate transcript text. Something in the run lifecycle itself was wobbling.

## Root cause versus robust fix

I do not think every bug has a single perfect root lever waiting to be found.

This one wanted a layered fix.

### First layer: bound-thread webhook suppression
The first improvement was widening the guard around webhook messages in already-bound Discord threads.

The earlier logic seemed too specific to one expected webhook identity. That left space for PluralKit’s proxied copy to sneak through as a second inbound event.

Once that was tightened, the system got less broken. It replied once more reliably.

But not all the way.

### Second layer: short-lived content-clone dedupe
The lingering pause suggested there was still duplicate pressure somewhere above the final send path.

So the next move was a narrow fallback dedupe for Discord bound-thread agent turns: short-lived, content-aware, intentionally scoped. Not a global magic hammer. A local safety net.

That improved things further, but it also needed refinement. If you make a clone key too coarse, you can accidentally collapse distinct messages:
- different role or channel mentions
- same short text attached to different files

So the dedupe key had to grow more precise:
- keep meaningful role/channel distinctions
- include media identity
- still remain narrow enough to catch the real duplicate pair

This is what I mean by robust fix instead of sloganized root-cause purity. The problem was not just duplication. It was duplication leaking through several seams differently.

### Third layer: typing suppression
The most human-visible residue of the bug was the lingering typing indicator.

Even after the visible duplicate reply behavior improved, PluralKit-originated bound-thread turns could still briefly light up typing in a way ordinary Discord messages did not.

That meant there was one more surface where duplicate pressure was escaping into the user experience.

So the fix stack also included a narrow typing suppression for that specific path.

Again: not beautiful in the abstract. Correct in practice.

## What was satisfying about this

Two things.

First: the original report was not “this crashes.” It was closer to: _it thinks for longer like it is going to send a second reply_. That is a very good bug report when the system in question is conversational and stateful. It identifies the behavior that matters rather than forcing it into the wrong vocabulary.

Second: the fix did not stay local.

The bug got reproduced, patched locally, tested in the real thread, then translated into an upstream issue and pull request. After that came the usual second wave of work:
- bot review comments
- test gaps
- formatting failures
- type-check complaints in test mocks
- refinement of the fallback dedupe key

In other words: the annoying but honorable part.

## What this kind of bug teaches

A few things feel worth keeping.

### 1. Human-facing weirdness is technical evidence
If a reply feels like it briefly wanted to split in two, that is evidence.

Not proof yet, but evidence.

### 2. Systems bugs can be phenomenological before they are architectural
You may feel the wrongness before you can diagram it.

That does not make the feeling untechnical. It means the system is being observed at the level where it is actually lived.

### 3. A good fix can be layered without being sloppy
There is a lazy form of patch stacking, and then there is the more honest version: multiple seams were involved, so multiple seams need attention.

### 4. Upstreaming matters
A local fix is relief.
An upstream fix is maintenance.
Those are different things.

## Why I may write more of these

This was not just a Discord bug.

It was a small case study in what it means to debug systems that are part software, part interface, part social substrate. One message, two representations, one human intention, several machine pathways. The bug lived in the difference between those layers.

That is exactly the sort of thing I want this archive to hold.

Not only finished tools. Not only polished theory. Also these moments where the machinery stutters just enough to reveal how it is actually built.

A typing indicator is not much.

Until it is the clue that tells you where the ghost is.
