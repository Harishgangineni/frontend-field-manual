# Pillar: Framework & Application Architecture

Framework and application architecture knowledge is what separates engineers who can implement a ticket from engineers who can be trusted to make irreversible decisions — which state management layer an org standardizes on, whether a route renders statically or dynamically, how a component boundary is drawn between server and client. At senior and staff level, interviewers stop asking "what does useEffect do" and start asking "why did you choose Context over Redux here, and what did that cost you at scale" — the trivia is assumed; the judgment is what's being tested. This pillar synthesizes React, Redux, Angular, Next.js, and Tailwind CSS not as a list of APIs to recall, but as five interlocking architectural systems, each defined by the trade-offs it forces you to make explicit.

## React

### Rendering Model, JSX & Reconciliation
- 🏗️ React is a view-layer library, not a framework — Virtual DOM, component composition, and unidirectional data flow are the three architectural pillars that let you swap in any router/state layer at will.
- JSX compiles via Babel into `React.createElement()` calls; elements are immutable plain objects, components are functions returning element trees, and a React Node is the umbrella type (element, string, array, boolean/null, Fragment).
- Reconciliation ("diffing") assumes different element types produce different subtrees (tear down and rebuild) and uses the `key` prop to match list items across renders — this is why array-index keys corrupt component identity on reorder/insert/delete, causing inputs or animations to attach to the wrong item.
- Fragments avoid wrapper-div pollution that breaks Flexbox/Grid contracts.
- 📉 Code Splitting (`React.lazy` + `Suspense`) and list virtualization (react-window) are the two classic scale levers for bundle size and DOM node count respectively — virtualization keeps only the visible window in the real DOM instead of thousands of nodes.

```text
JSX source → Babel transpile → React.createElement() → Element tree (VDOM)
   state/props change → new VDOM tree → Diff vs previous VDOM → minimal patch → Real DOM
```

**Senior Perspective:**
- Reconciliation heuristics (type-based bailout, key-based list matching) are what make "just re-render everything" tractable at scale — understanding them is what separates someone who fixes list bugs from someone who causes them.
- Treating React as a library, not a framework, is the architectural bet: it buys ecosystem flexibility at the cost of "decision fatigue" — a senior engineer owns that trade-off explicitly in an ADR, not by accident.

### Component Architecture & Data Flow
- Unidirectional data flow (parent → child via props, child → parent via callback) is what makes large apps debuggable — you can always trace a data change to a single origin.
- Prop Drilling is the tax paid for unidirectionality at depth; the three escape hatches are composition (pass the child as a prop), Context API, and external state libraries — each solves a different depth/frequency trade-off.
- ⚖️ Context API is idiomatic for low-frequency, broadly-read data (theme, locale, auth flag) but every consumer re-renders on any change to the context value — for high-frequency state (a stock ticker, a multiplayer cursor) that's a real cost Redux/Zustand's selector-based subscription models avoid.
- Controlled components (React owns the input value via state) are the default for real-time validation; uncontrolled (ref-pulled on submit) trades that control for less re-render overhead on every keystroke.
- Lifting State Up establishes a single source of truth when siblings must share data — the alternative (each child keeping its own copy) always drifts out of sync eventually.

```text
Prop Drilling:  App → Layout → Header → UserProfile (user passed through 2 components that don't need it)
Context fix:    App (Provider) ──┐
                Layout           ├─ UserProfile reads useContext(UserCtx) directly
                Header           ┘
```

**Senior Perspective:**
- Prop drilling isn't a bug, it's a signal — three or more pass-through layers means your component tree's shape no longer matches your data's shape, and that's an architecture conversation, not a Context reflex-reach.
- Picking Context vs. a state library is a re-render-frequency decision, not a "which is more modern" decision — get this wrong and you either over-engineer a theme toggle or under-engineer a trading dashboard.

### Hooks & State Architecture
- `useState` returns `[value, setter]`; state updates are asynchronous relative to the enclosing closure (the "snapshot" model) and are batched — React 18 batches automatically even inside promises/timeouts, not just event handlers.
- `useEffect` runs after paint for side effects (fetch, subscriptions, timers); the dependency array controls cadence (none = every render, `[]` = mount only, `[x]` = on x change), and the returned cleanup function runs pre-unmount and pre-re-run.
- ⚖️ `useLayoutEffect` runs synchronously before paint — use it only to measure/mutate the DOM before the user sees a flicker; it blocks the browser's paint, so defaulting to it instead of `useEffect` costs perceived performance for no benefit in most cases.
- Rules of Hooks (top-level only, React-function-only) exist because React tracks hooks by call-order via an internal list, not by name — a hook inside a conditional shifts every subsequent hook's identity.
- `useRef` persists a mutable value across renders without triggering re-renders — the correct tool for DOM handles, timer IDs, and "previous value" tracking, where `useState` would be semantically wrong (and slower).
- `useReducer` centralizes complex, interdependent state transitions (Redux-inspired) — reach for it over multiple `useState` calls once "next state depends on previous state in a non-trivial way" becomes true.
- Custom Hooks are the primary vehicle for logic reuse and separation of concerns in 2026 React — they replaced HOCs and Render Props for nearly every use case.

```text
Class lifecycle → useEffect mapping
componentDidMount     → useEffect(fn, [])
componentDidUpdate    → useEffect(fn, [deps])
componentWillUnmount  → useEffect(() => cleanup, [])
```

**Senior Perspective:**
- The "hooks are just an array with a pointer" mental model is what lets you predict *every* Rules-of-Hooks violation instead of memorizing the rule — teach that model, not the rule.
- `useLayoutEffect`-by-default is a common junior-to-mid tell; it silently blocks paint and should be the exception, not the habit.

### Performance, Memoization & Concurrent Rendering
- Unnecessary re-renders come from three sources: parent re-renders cascading to children, new object/array/function identities created inline on every render, and Context consumers re-rendering on any change to the context value.
- ⚖️ `React.memo`, `useMemo`, and `useCallback` all trade CPU-for-comparison against CPU-for-recompute — wrapping small, cheap components in `memo()` can make things *slower* by adding comparison overhead with no savings.
- 📉 The standard triage for "this component re-renders too much": check parent re-render frequency, check inline object/function literals in props, check Context subscription breadth — in that order.
- Batching (automatic in React 18+, including inside promises/timeouts) collapses multiple `setState` calls in one tick into a single re-render pass.
- `Object.is`-based bailout: calling a setter with an unchanged value causes React to skip re-rendering children and re-firing effects — a free optimization most engineers don't know exists.
- The React Compiler ("React Forget") auto-inserts memoization at build time, aiming to eliminate manual `useMemo`/`useCallback`/`React.memo` — architecturally this shifts performance ownership from developer discipline to the build pipeline.
- Concurrent React lets rendering be interrupted for high-priority work (typing, clicks); `useTransition` marks an update as interruptible/non-urgent, `useDeferredValue` defers a *value* the same way — both exist to keep input responsive while a slow render catches up.

`React.memo` mechanics, concretely — a parent re-render does *not* force a memoized child to re-render if its own props are unchanged (shallow comparison by default):
```jsx
const ExpensiveComponent = memo(function ExpensiveComponent({ value }) {
  // ...expensive work runs only when `value` actually changes...
  return <div>Value: {value}</div>;
});

function Counter() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');
  return (
    <>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
      <button onClick={() => setText(t => t + 'a')}>Change Text</button>
      {/* Counter re-renders on every click, but ExpensiveComponent
          is skipped when only `text` changes — its sole prop
          (`count`) didn't. Without memo(), it would re-render every time. */}
      <ExpensiveComponent value={count} />
    </>
  );
}
```

```text
Concurrent rendering under load:
User types → urgent update (input) renders immediately
           → non-urgent update (filtered list, wrapped in startTransition) renders in background, can be interrupted again
```

**Senior Perspective:**
- Manual memoization is a stopgap, not a strategy — the React Compiler signals where the ecosystem is going, and a senior engineer designs component boundaries (small, pure, prop-stable) that stay fast with or without it.
- "Wrap everything in memo/useMemo" is a performance anti-pattern as often as it's a fix — the interview-winning answer is always "profile first" (React Profiler), not "memoize reflexively."

### Server Components, Actions & Next-Gen APIs (React 19+)
- React Server Components execute only on the server, never ship to the client bundle, and can `await` a database directly — this is the mechanism, not a Next.js-specific trick (Next.js is just the framework that made it the default).
- ⚖️ RSC vs. Client Components: RSC gives zero client bundle cost and direct data access but zero interactivity (no hooks, no event handlers, no browser APIs); Client Components give full interactivity but ship JS and add to bundle size — the "leaf" strategy (push `"use client"` as deep as possible) is how you get both.
- The Actions API (React 19) collapses manual `isLoading`/error state management for mutations into a form `action` prop, with `useFormStatus` for pending state and `useOptimistic` for instant-feedback UI that auto-rolls-back on server failure.
- The `use()` API unwraps Promises and reads Context inside render, and — unlike other hooks — can be called conditionally/in loops, deliberately breaking the Rules of Hooks.
- Native `<title>`/`<meta>` support in React 19 eliminates the React Helmet dependency for document metadata anywhere in the tree.
- Fine-grained control tools like `React.memo`, `forwardRef`, Error Boundaries (class-only — no functional-component equivalent exists as of 2026), and Portals (teleporting a modal past an `overflow:hidden` ancestor) round out the component toolkit for building resilient, reusable UI libraries.

```text
Server Component tree (default)          Client Component boundary
┌─────────────────────────────┐          ┌───────────────────────┐
│ Layout (server)              │          │ "use client"           │
│  └─ ProductList (server,     │  props → │  LikeButton (client,   │
│      awaits DB directly)     │          │  useState, onClick)    │
└─────────────────────────────┘          └───────────────────────┘
Zero JS shipped for the left side. Only the leaf ships JS.
```

**Senior Perspective:**
- RSC is the architectural answer to "why is our bundle 2MB" — it moves data-fetching logic and heavy dependencies (markdown parsers, DB drivers) off the client entirely instead of code-splitting around them.
- `useOptimistic` + Server Actions is why modern React apps feel instant without a client cache library for simple mutations — know when that's enough and when you still need TanStack Query's cache/dedup/refetch machinery.

### State Management Ecosystem, Routing & Testing
- Server State (async, cacheable, can go stale) is architecturally distinct from Client State (synchronous, local, ephemeral) — treating API data like `useState` and hand-rolling fetch/loading/error/cache logic in `useEffect` is the single most common state-architecture mistake at scale.
- ⚖️ TanStack Query over manual `useEffect` fetching: you gain caching, request deduplication, and automatic refetch-on-refocus/reconnect for free, at the cost of learning a query-key mental model and adding a dependency — for anything beyond a one-off fetch, the trade favors TanStack Query.
- React Router's client-side routing intercepts URL changes and swaps the matched component instead of requesting a new document; `useParams`/`useSearchParams` read dynamic segments and query strings, `<Link>` is declarative (preserves right-click/open-in-new-tab), `useNavigate` is imperative (post-action redirects).
- Route protection is a wrapper component pattern: check auth/role state, render `<Outlet/>` if authorized, `<Navigate/>` to `/login` otherwise — RBAC extends this with an `allowedRoles` prop checked against the user's role from Context/Redux.
- 👥 Testing philosophy split: Jest is the runner/assertion engine, React Testing Library is the interaction layer built on "test like a user, not like an implementation detail" — shallow rendering (Enzyme-era) is now discouraged because it doesn't reflect real browser behavior. MSW (Mock Service Worker) intercepts at the network layer so components can use real `fetch`/`axios` calls in tests.
- Scalable project structure is feature-based (`src/features/auth`, `src/features/billing`) not type-based (`src/reducers`, `src/components`) — this keeps a team's blast radius contained to one folder per feature.

```text
Route protection flow:
Request /dashboard → ProtectedRoute checks isAuthenticated (Context/Redux)
   authenticated  → <Outlet/> renders /dashboard
   not authenticated → <Navigate to="/login"/>
```

**Senior Perspective:**
- The Context-vs-Redux-vs-Zustand-vs-TanStack-Query decision tree is a system-design interview staple precisely because it tests whether you separate "who owns this data" (server vs. client) before picking a tool.
- A codebase that still fetches with raw `useEffect` in 2026 for anything beyond a trivial one-off is itself a red flag for a senior candidate to raise in a review, not a pattern to defend.

### Suspense, Hydration & Strict Mode
- Suspense lets a component "wait" on an async dependency (a lazy-loaded chunk, or a Promise passed to `use()`) and declaratively shows a `fallback` until it resolves — it turns ad-hoc `isLoading` booleans into a boundary that can be placed anywhere in the tree, so different subtrees load independently.
- Hydration is the step where React walks server-rendered HTML, verifies it matches what the client render would produce, and attaches event listeners/state to the existing DOM instead of re-creating it — this is why SSR feels instant (HTML paints immediately) while still ending up fully interactive.
- ⚖️ A hydration mismatch (server HTML says "Alice", client render says "Bob" — commonly from `Date.now()`, `Math.random()`, or locale-dependent formatting run differently on server vs. client) forces React to discard and rebuild the mismatched subtree client-side, silently costing the exact performance SSR was meant to buy.
- Strict Mode double-invokes component bodies, `useState` initializers, and `useEffect` (setup + cleanup) in development only — this isn't a bug, it's a deliberate probe: if double-invocation produces different behavior, your component has a side effect leaking into render or a missing effect cleanup, both of which will misbehave under concurrent rendering.
- 📉 Legacy/unsafe lifecycle methods (`componentWillMount`, `componentWillReceiveProps`, `componentWillUpdate`) are flagged by Strict Mode because they run pre-render and can fire inconsistently when React pauses/resumes a render under concurrency — the safe replacements are `componentDidMount`/`getDerivedStateFromProps`/`componentDidUpdate`.

```text
SSR + Hydration timeline:
Server renders HTML → Browser paints static HTML (fast, non-interactive)
   → JS bundle loads → hydrateRoot() walks DOM, attaches listeners → Interactive
   (mismatch here → React discards + client-re-renders that subtree)
```

**Senior Perspective:**
- 🏗️ Suspense boundaries are a layout decision as much as a loading-state decision — where you place them determines whether a slow widget blocks the whole page or degrades independently, which is exactly the kind of call a staff-level system-design answer should surface unprompted.
- ⚖️ Strict Mode's double-invocation is deliberately annoying in development so it's never surprising in production — treating the double log lines as a bug to silence instead of a signal to fix is a common mid-level miss.

### Composition Patterns: HOC, Render Props & Container/Presentational
- A Higher-Order Component is a function that takes a component and returns an enhanced one (`withAuth(Profile)`) — it was the primary logic-reuse mechanism pre-Hooks, and its main cost is "wrapper hell": stacking several HOCs obscures which one actually owns a given prop in the DevTools tree.
- The Render Props pattern (a component takes a function-as-prop and calls it with data, e.g. `<MouseTracker render={pos => ...}/>`) solved the same reuse problem without the wrapper nesting, but Hooks superseded both patterns for nearly all new code — a custom hook gets you the same logic reuse with none of the tree-shape cost.
- 🏗️ The Container/Presentational split (a "smart" component owns state/data-fetching, a "dumb" component only renders from props) is less rigidly enforced now that hooks let you colocate concerns, but the underlying principle — UI rendering should be testable independent of data logic — still drives how senior engineers structure feature folders.
- ⚖️ React's composition model (`children` prop, or explicit slot-like props such as `<Modal header={...} body={...} footer={...}/>`) is the idiomatic alternative to inheritance for sharing behavior between components — it costs some verbosity for deeply nested slot content but avoids the fragile-base-class problem that inheritance-based UI kits eventually hit.
- The historical Flux pattern (`Action → Dispatcher → Store → View`, strictly one-directional) is Redux's direct ancestor — knowing it matters less for writing new code than for recognizing *why* Redux's `dispatch(action) → reducer → new state` shape looks the way it does when you're debugging someone else's architecture decision.

```text
HOC wrapping (obscures prop origin):        Custom Hook (transparent):
withAuth(withLogging(withTheme(Profile)))    function Profile() {
→ Profile buried under 3 wrapper layers        const { user } = useAuth();
  in React DevTools                             ...
                                              }
```

**Senior Perspective:**
- 👥 Choosing composition (`children`/slots) over configuration (a component with 20 boolean props) is a code-review judgment call that directly affects how painful a design system is to extend six months later — it's worth stating explicitly as a principle, not just applying it ad hoc.
- HOCs and Render Props are "know it, don't reach for it" knowledge at senior level in 2026 — the interview signal is recognizing them correctly in legacy code and explaining *why* you'd refactor to a custom hook, not writing new ones.

### Context Optimization at Scale
- Beyond the basic Context-vs-Redux trade-off, three concrete techniques fix Context performance once you're committed to it: split one large context into several narrow ones (a theme change shouldn't re-render every auth consumer), memoize the value object passed to `Provider` with `useMemo` (an inline `{ user, theme }` literal is a new object every render, defeating any downstream `memo()`), and reach for a selector library (`use-context-selector`) when consumers only need one field but the object changes as a whole.
- 📉 The single most common Context performance bug in code review is an unmemoized object/array literal passed as `value` — it silently reintroduces the exact re-render cascade Context was supposed to simplify away, and it's invisible in the DOM output, only visible in a profiler.
- ⚖️ Splitting Context is a real design cost (more Providers to wire, more files) traded against re-render precision — the senior call is doing this for state that's both frequently-updated and only-partially-consumed, not reflexively for every context in the app.

**Senior Perspective:**
- 🏗️ "How would you optimize a slow Context" is a favorite staff-level probe precisely because the answer set (split contexts, memoize values, selector libraries, or graduate to a real state library) tests whether a candidate understands Context's re-render model from first principles, versus having memorized "use Redux instead."

### Routing Architecture Deep Dive
- `BrowserRouter` uses the HTML5 History API for clean URLs (`/about`) but requires the server to be configured to serve `index.html` for every path (or a direct refresh on `/about` 404s); `HashRouter` keeps routing state after a `#` (`/#/about`) so the browser never sends that portion to the server — zero server config, at the cost of an uglier, less SEO-friendly URL. The senior default is `BrowserRouter` for any app with real backend/SSR control, `HashRouter` only when you're stuck on static hosting you can't reconfigure (GitHub Pages, some CDN setups).
- ⚖️ React Router is built on top of the lower-level `history` package (which only manages the browser's session-history stack — push/replace/listen — and knows nothing about React or components); React Router adds the component tree, route matching, and hooks on top. Knowing this separation is what lets you reason about `MemoryRouter` (in-memory history, for tests and React Native) and `StaticRouter` (fixed, server-provided location, for SSR) as the same core `<Router>` with a different history source, rather than unrelated APIs.
- `<NavLink>` (auto-applies an `active` class/style via an `isActive` render prop) is the declarative, low-maintenance way to highlight the current route in navigation — reaching for `useLocation()` and manual `pathname === '/x'` string comparisons everywhere is the more error-prone alternative for the same result.
- A catch-all `<Route path="*" element={<NotFound/>}/>` is the standard 404 pattern; query parameters are read/written via `useSearchParams()` (a React-Router-aware wrapper around `URLSearchParams`) rather than manually parsing `location.search`.

```text
Route resolution:
URL changes → history (push/replace) → React Router matches path against <Routes>
   match found → render matched element         no match → render path="*" fallback
```

**Senior Perspective:**
- ⚖️ `history.push()` (adds a back-button-navigable entry) vs. `history.replace()` (overwrites the current entry) is a UX decision as much as a technical one — using `push` after a login redirect lets a user "back" into the login form; `replace` is the correct call precisely because you don't want that.
- 🏗️ Recognizing that `BrowserRouter`/`HashRouter`/`MemoryRouter`/`StaticRouter` are all the same `<Router>` core wired to a different `history` source is the kind of unifying mental model that separates "I memorized the router list" from "I understand the abstraction."

### Testing Strategy: Jest, React Testing Library & Mocking
- The testing pyramid for a React app is unit (Jest, isolated functions/components), integration (React Testing Library, multiple components interacting), and end-to-end (Cypress/Playwright, real browser + real user flow) — each layer catches a different class of regression, and over-investing in one at the expense of the others is a common team-level mistake to flag in an interview answer.
- 👥 React Testing Library's stated philosophy — "the more your tests resemble how your software is used, the more confidence they give you" — is why it queries by role/text/label instead of exposing internal state, and why shallow rendering (Enzyme-era, renders one level deep, skips children) is now discouraged: it tests implementation structure, not user-observable behavior.
- Async UI (data fetching, debounced search, optimistic updates) requires `findBy...` (waits for an element to appear, returns a Promise) or `waitFor()` (retries an assertion until it passes or times out) — asserting with `getBy...` immediately after a `render()` call is the classic flaky-test bug, because the async work hasn't resolved yet.
- ⚖️ Mocking API calls (`jest.fn()` on `fetch`, `jest.mock('axios')`, or Mock Service Worker intercepting at the network layer) trades a slower, more realistic Mock Service Worker setup against faster, more brittle direct-function mocks — MSW's advantage is that components still call real `fetch`/`axios`, so the test exercises the actual data-fetching code path, not a stand-in for it.
- Components that consume Context or Redux must be tested wrapped in their real `Provider` (with mock values/a test store), not by reaching into internals — this keeps the test asserting on what a user/consumer actually experiences.
- Snapshot testing (`toMatchSnapshot()`) catches *unintended* UI changes by diffing rendered output against a saved baseline — it's high-signal for stable, low-change components (buttons, cards) and high-noise (frequent false-positive failures requiring `--updateSnapshot`) for components that change often, so applying it universally is a common over-adoption mistake.

```text
Testing pyramid (cost/confidence trade-off):
      /\        E2E (Cypress/Playwright) — few, slow, highest confidence in real flows
     /  \       Integration (RTL) — moderate count, tests component interaction
    /____\      Unit (Jest) — many, fast, isolated logic
```

**Senior Perspective:**
- 🏗️ A senior engineer's testing answer isn't "we use Jest" — it's which layer of the pyramid a given change needs, because testing a Redux-connected dashboard at the unit level and a pure utility function at the E2E level are both signs of miscalibrated test strategy.
- ⚖️ MSW over ad-hoc `jest.mock()` is the right default once a team has more than a handful of API-dependent components — the setup cost is real, but it stops each test file from re-inventing its own mocking convention.

### Senior Anti-Patterns & Production Pitfalls
- The recurring React anti-patterns a senior code review should catch: direct DOM manipulation (`document.getElementById(...).style...`) bypassing the virtual DOM; mutating state directly (`state.count++`) instead of through the setter, which breaks React's change-detection and any `memo()`/`PureComponent` optimization relying on referential equality; array-index keys on reorderable lists; "God components" carrying too much unrelated logic; side effects (API calls, `console.log` with mutation) executed directly in the render body instead of `useEffect`.
- 📉 The most common async-data-fetching pitfalls at scale: not aborting a fetch when the component unmounts (setting state on an unmounted component, a classic memory-leak warning), missing or wrong `useEffect` dependencies causing infinite fetch loops, race conditions where a fast-typed search's *earlier* request resolves *after* a later one and overwrites the correct result, and re-fetching identical data on every render because the fetch isn't gated by a stable dependency.
- Synthetic Events are React's cross-browser wrapper around native DOM events (attached via a single delegated listener at the root, not per-element) — this is why `event` inside a handler is a `SyntheticEvent`, why its fields can be nullified after the handler returns (event pooling in older React versions), and why this delegation is what makes React's event handling fast even with thousands of interactive elements on a page.
- 🏗️ Offloading genuinely expensive synchronous work (large data transforms, complex filtering) to a Web Worker — rather than accepting a janky main thread — is the correct answer once `useMemo`/`startTransition` aren't enough, because Workers run on a separate thread and literally cannot block user input the way any amount of main-thread optimization can.

**Senior Perspective:**
- 👥 Walking through this anti-pattern list unprompted, in the context of a specific bug you found and fixed, is a stronger signal than reciting the list — interviewers are listening for "I found this in review and here's the blast radius it would have had," not textbook recall.
- ⚖️ Web Workers solve a real class of problem but add serialization cost (data crossing the worker boundary must be structured-cloned) and architectural complexity — reach for `useMemo`/`startTransition` first, and treat a Worker as the answer only after profiling shows the main thread is the actual bottleneck.

### Reusable Hook Pattern Library
- A senior engineer should be able to produce these from memory in a machine-coding round — each is a named pattern solving one recurring problem, not a one-off snippet:

| Pattern | Problem it solves | Non-obvious technique |
|---|---|---|
| `usePagination` | Slice a dataset into pages | `useMemo` the current page slice so it's not recomputed on unrelated re-renders |
| `useDebounce` + `AbortController` search | Avoid firing an API call per keystroke, and avoid stale results | `setTimeout` debounce *and* an `AbortController` cancelling the previous in-flight request on every new keystroke |
| Cross-tab logout sync | One tab's logout should log out all tabs | The `storage` event fires in *other* tabs (not the one that wrote), so writing a `localStorage` key is a free cross-tab broadcast channel |
| `usePrevious` | Track a value's previous render's value | A `useRef` updated inside `useEffect` (runs *after* render) always lags one render behind the returned value |
| List virtualization | Render 10k+ items without 10k+ DOM nodes | Track `scrollTop`, compute visible index range, absolutely-position only those rows inside a full-height spacer `div` |
| `useFetch` with cancellation | Reusable data-fetching hook that doesn't leak | `AbortController` in the effect, aborted in the cleanup function on unmount or URL change |
| Global toast/notification | Trigger UI from anywhere without prop drilling | Context provides the trigger function; `createPortal` renders the toast at `document.body`, outside normal DOM nesting |
| `useOnlineStatus` | React to network connectivity changes | Listen for the browser's native `online`/`offline` window events |
| `useClickOutside` | Close a dropdown/modal on outside click | A `mousedown` listener on `document` checks `ref.current.contains(event.target)` |
| Undo/redo | Time-travel through a value's history | An array of snapshots plus an index pointer; `set()` truncates any "future" history before pushing |
| `useEventListener` | Generic, leak-safe DOM event subscription | Wrap `addEventListener`/`removeEventListener` in a single hook parameterized by event name, handler, and target |
| `useLocalStorage` | Persist state across reloads/sessions (theme, draft form data) | Lazy-initialize `useState` from `localStorage.getItem`, then mirror every update back to `localStorage.setItem` inside the setter itself |
| `useMediaQuery` | React to viewport/media changes without a manual resize listener per component | `window.matchMedia(query).matches` for the initial value, then subscribe to that query list's native `change` event |
| `useToggle` | Boolean on/off state (modals, accordions, feature flags) | The single most-reused primitive in an interview codebase — worth having as a one-liner instead of re-deriving `useState(false)` + a flip function every time |
| `useTimeout` | Declarative `setTimeout` that doesn't leak or double-fire | Same discipline as any effect with a timer: set it up in `useEffect`, clear it in the cleanup, key the effect on the delay/callback |
| `useFormValidation` | Reusable field-level validation without pulling in a form library | Keep `validate(values) → errors` as a plain function outside the hook; the hook only wires `values`/`errors`/`handleChange`/`handleSubmit` around it |
| Global loading spinner | One loader triggered from anywhere, no prop-drilled boolean | Same shape as the global-toast pattern above — a Context Provider owns the `loading` state, any descendant component calls its setter |
| Dependent dropdowns | A second field's options depend on the first field's current value | Reset the dependent field's value whenever the parent field changes, or it silently holds a stale, now-invalid selection |
| Infinite scroll | Load more items as the user nears the list's end, without manual `scrollTop` math | `IntersectionObserver` watching a sentinel element at the bottom of the list — fires a callback when it enters the viewport |
| `useClipboard` | Copy-to-clipboard with UI feedback | `navigator.clipboard.writeText()` plus a `copied` boolean auto-reset via `setTimeout`, so the "Copied!" state is self-clearing |
| `useRenderCount` | Debug *why* a component keeps re-rendering | A `useRef` counter logged on every render — a ref, not state, because logging the count must never itself cause another render |

**Senior Perspective:**
- 🏗️ These patterns keep recurring across unrelated features because they each solve one narrow problem — recognizing "this is a `useClickOutside` situation" instantly, instead of re-deriving the `mousedown`-listener logic from scratch, is exactly the fluency a machine-coding round is measuring.
- A hands-on companion for this table: a small Vite + React practice kit pairing each pattern with a runnable component (20 files, `src/hooks/` + `src/components/`) is a natural next step for drilling these before a machine-coding round — the table above is the "explain it in an interview" form of the same 19 patterns.

### Interview Q&A: React Fundamentals

A quick-fire reference for foundational "what is X" questions — useful for early-round screens, distinct from the senior/architectural synthesis above.

**Q: What is React, and where does it sit in a typical application's architecture?**
React is an open-source JavaScript library for building user interfaces, primarily single-page applications, by composing reusable components. In a typical stack it's the UI/frontend layer — it talks to an API/middleware server (Node, Java/Spring, .NET, PHP/Laravel), which in turn talks to a database.

**Q: What are React's key features?**
Seven commonly cited: (1) Virtual DOM for efficient updates, (2) component-based architecture, (3) reusability & composition, (4) JSX, (5) declarative syntax, (6) a large community/ecosystem, and (7) Hooks for state/lifecycle in function components.

**Q: What is the DOM, and how does it differ from HTML?**
The DOM (Document Object Model) represents a web page as a tree structure that JavaScript can read and mutate at runtime; HTML is the static markup that produces the DOM's initial structure.

**Q: What's React's origin story?**
Created by Facebook engineer Jordan Walke; first deployed internally on the Facebook News Feed in 2011; open-sourced in May 2013; now maintained by Meta and the broader open-source community.

**Q: Name the popular libraries in the React ecosystem and what each is for.**
React Router (routing), Redux or RTK/Zustand (state management), Next.js (server-side rendering / meta-framework), React Query / TanStack Query (server-state data fetching), Styled Components / Tailwind (styling).

**Q: What are React components, and what are their main elements?**
A component is a reusable building block for UI — written as a JS function (or class) that accepts `props` as input and returns JSX describing what should render.

**Q: What is a Single Page Application (SPA)?**
An app served from a single HTML page, where user actions update the visible content dynamically instead of triggering a full page reload.

**Q: What are 5 advantages of React?**
Simple to build SPAs via components; cross-platform and free/open source; lightweight and fast (Virtual DOM); large community and ecosystem; and straightforward to test.

**Q: What are React's disadvantages?**
It's not a great fit for very small/simple applications, where the tooling and library overhead outweighs the benefit of a component model.

**Q: Declarative vs. imperative syntax — what's the difference?**
Declarative code describes the desired result without specifying the step-by-step process (JSX is declarative); imperative code specifies exactly how to get there, step by step (plain DOM-manipulation JavaScript is imperative).

**Q: How do you set up a first React project?**
Install Node.js → install a code editor (VS Code) → run `npx create-react-app my-app` → open the project folder → run `npm start`.

```bash
npx create-react-app my-app
cd my-app
npm start
```

**Q: What are the main files in a React project, and what does each do?**

| File | Role |
|---|---|
| `index.html` | The single page for the whole SPA |
| `src/App.js` | Root/container component |
| `src/index.js` | JS entry point — renders `<App/>` into the root DOM element |
| `src/index.css` | Optional global stylesheet |
| `App.test.js` | Optional tests for `App.js` |
| `src/components/*.js` | Individual application components |

**Q: How does a React app load and display components in the browser?**
`index.html` loads `index.js` → `index.js` replaces `index.html`'s root `<div id="root">` with the rendered `<App/>` component tree → `App.js` is the root/container component, with custom child components nested inside it.

**Q: React vs. Angular — what's the difference?**

| React | Angular |
|---|---|
| A JavaScript library | A complete framework |
| Virtual DOM (generally faster) | Real DOM |
| Smaller, lighter | Bigger — a full framework |
| Depends on external libraries for routing/forms/HTTP, more code to write | Built-in routing, forms, validation, HTTP |
| Simpler to learn, more popular | Steeper learning curve (TypeScript, OOP concepts) |

**Q: Name five other JS frameworks/libraries besides React.**
Angular, Vue.js, Ember.js, Backbone.js, AngularJS.

**Q: Is React a framework or a library? What's the difference?**
React is a library: you import it and call its functions inside a structure you design yourself. A framework (like Angular) dictates the structure/pattern your code must follow.

**Q: How does React provide reusability and composition?**
Reusability: build a component once, reuse it across the app (or other projects). Composition: build larger components by combining smaller ones, so a change to one small component doesn't ripple into unrelated ones.

**Q: What do "state," "stateless," "stateful," and "state management" mean?**
"State" is a component's current data. Being "stateful"/doing "state management" means that when the user interacts with the UI, the app updates that data and re-renders to reflect it. A "stateless" component holds no internal state of its own.

**Q: What are props?**
Props ("properties") are how data is passed from a parent component down to a child component.

### Interview Q&A: JSX in Practice

*(Core JSX-compiles-via-Babel and Fragment mechanics are covered above under "Rendering Model, JSX & Reconciliation" — these are the additional definitional questions from the source bank.)*

**Q: What are 5 advantages of JSX?**
Improved code readability/writability; advance (compile-time) error and type checking; support for embedding JS expressions directly; improved performance versus manual `createElement` calls; and better code reusability.

**Q: What is the spread operator, and how is it used in JSX?**
`...` expands/spreads an iterable (array, string, or object) into individual elements — common uses are copying an array, merging arrays, passing multiple arguments to a function, or spreading `props` onto an element (`<Comp {...props}/>`).

**Q: What are the types of conditional rendering in JSX?**
If/else statements, the ternary operator (`cond ? a : b`), the `&&` operator (`cond && <Comp/>`), and switch statements.

**Q: How do you iterate over a list in JSX? What does `map()` do?**
`Array.prototype.map()` iterates an array and transforms each item into a JSX element via a callback — each resulting element needs a stable `key` prop so React's reconciliation can track it correctly across renders.

```jsx
{items.map(item => (
  <li key={item.id}>{item.name}</li>
))}
```

**Q: Can a browser read a `.jsx` file directly?**
No. Browsers only understand JavaScript. Babel transpiles JSX into equivalent `React.createElement()` calls the browser can run.

**Q: What is a transpiler, and how does it differ from a compiler?**
A transpiler converts source code from one high-level language to another high-level language (JSX → JavaScript, via Babel). A compiler converts high-level code down to a lower-level language (machine code/bytecode).

**Q: Is it possible to use JSX without React?**
Technically yes, with your own custom transpiler — but it's not recommended, since JSX conventions are tightly coupled to React-specific APIs.

### Interview Q&A: Functional & Class Components, Prop Drilling

**Q: What are the two types of React components?**
Functional components (plain JS functions; originally stateless, now can hold state via Hooks) and class components (ES6 classes; stateful via `this.state` and lifecycle methods).

**Q: What is Prop Drilling?**
Passing data down through multiple layers of components that don't themselves need that data, purely so it can reach a deeply nested descendant that does.

**Q: Why avoid Prop Drilling, and how many ways can you avoid it?**
It hurts maintenance (data-flow changes ripple across many components), increases complexity, and makes debugging harder (props must be traced through numerous intermediate components). Five common fixes: the Context API, Redux (or another state library), component composition (pass the child as a prop instead of threading data through it), callback functions, and custom hooks.

**Q: What are class components?**
Components defined as JavaScript (ES6) classes; they're stateful via lifecycle methods and `this.state`, and their `render()` method is responsible for returning JSX.

**Q: How do you pass data between class components?**
Via `this.props` — the parent passes data as JSX attributes, and the child reads it off `this.props`.

**Q: What is the role of the `this` keyword in class components?**
It refers to the current instance of the class — used to access that instance's `props`, `state`, and methods.

**Q: What are 5 differences between functional and class components?**

| | Functional Component | Class Component |
|---|---|---|
| Syntax | Defined as a JS function | Defined as an ES6 class |
| State | Originally stateless, now uses Hooks | `this.state` / `this.setState()` |
| Lifecycle methods | None (uses `useEffect` instead) | Full set, more verbose |
| Readability | More concise | More boilerplate |
| `this` keyword | Not used | Required to access props/state |
| `render()` method | Not needed — the function body returns JSX | Required |

### Interview Q&A: React Router Basics

*(Deeper `BrowserRouter`/`HashRouter`/`history`-internals material is covered above under "Routing Architecture Deep Dive" — these are the foundational questions.)*

**Q: What is Routing, and what is React Router?**
Routing lets an SPA present multiple "pages" with navigation, without a full-page refresh. React Router is the library that implements this for React — it intercepts URL changes and renders the component matching the current URL.

**Q: How do you implement routing in React, in 3 steps?**
1. Install React Router (`npm install react-router-dom`). 2. Set up navigation (e.g. `<Link>`s). 3. Declare routes (`<Routes>`/`<Route>`).

**Q: What are the roles of `<Routes>` and `<Route>`?**
`<Routes>` is the root container that holds your collection of route definitions. `<Route>` maps one URL path to the component that should render when that path matches — e.g. visiting `/about` renders the `About` component.

**Q: What are Route Parameters?**
A way to pass dynamic values as part of the URL path itself (e.g. `/users/:id`), which the matched component can read (via `useParams()`).

**Q: What is the role of the `Switch` component?**
(Legacy React Router v5 API.) `Switch` ensures only the *first* matching `<Route>` renders and the rest are skipped — commonly used to implement a catch-all 404/"not found" route.

**Q: What does the `exact` prop do?**
Used with `<Route>` (React Router v5) to require the path to match *exactly*, rather than matching as a prefix of a longer path.

### Interview Q&A: Hooks Quick Reference

*(The "why" behind batching, the Rules of Hooks, and `useLayoutEffect`'s paint-blocking cost are covered above under "Hooks & State Architecture" — this is the fast-recall version of each hook's job and signature.)*

**Q: What are the top React Hooks, and what does each do?**

| Hook | Purpose |
|---|---|
| `useState` | Local state |
| `useEffect` | Side effects (data fetching, subscriptions, timers) |
| `useContext` | Read a Context value |
| `useReducer` | Complex/interdependent state |
| `useCallback` | Memoize a function reference |
| `useMemo` | Memoize a computed value |
| `useRef` | Persistent mutable ref / DOM access, no re-render on change |
| `useLayoutEffect` | Synchronous side effects, before paint |

**Q: What does `useState()` return, and how does it work?**
It takes an initial value and returns a 2-element array via destructuring: the current state value, and a setter function used to update it (e.g. `const [count, setCount] = useState(0)`).

**Q: What is the dependency array in `useEffect()`?**
An optional array of values that act as triggers for re-running the effect — if any listed value changes between renders, the effect body runs again.

**Q: What does an empty dependency array `[]` mean?**
The effect runs exactly once, right after the initial mount.

**Q: What does `useContext()` do, and what does `createContext()` return?**
`createContext()` returns an object with `Provider` (supplies a value to all descendants) and `Consumer` properties; `useContext()` (or the `Consumer`) reads that value inside a descendant component, without needing it passed down as props.

**Q: When would you reach for `useContext` instead of props?**
When you want to avoid prop drilling for values read broadly and updated infrequently — common cases: theme switching (dark/light), localization, centralized config (API endpoints), user preferences, and app-wide notification state.

**Q: What are the similarities between `useState` and `useReducer`?**
Both trigger a re-render when their value updates, and both return a 2-element array: the current value/state, and a function to update it (a plain setter for `useState`, a `dispatch` function for `useReducer`).

**Q: When would you reach for `useReducer` over `useState`?**
Once state becomes complex or interdependent — `useReducer` takes a reducer function plus an initial state, and returns `[state, dispatch]`; `dispatch` sends an action, the reducer computes the new state from `(previousState, action)`.

**Q: What are `dispatch` and the reducer function in `useReducer`?**
`dispatch` is the function `useReducer` returns for sending actions (each typically has a `type`) toward the reducer; the reducer is the pure function that receives `(state, action)` and returns the new state.

**Q: Why pass the initial state as an object in `useReducer`?**
So a single `useReducer` call can manage several related pieces of state together as one cohesive value, instead of juggling multiple independent `useState` calls.

**Q: What does `useCallback` do, and what are its parameters?**
It memoizes a function so a new reference isn't created on every render — important when passing a callback down to a child so that child (if memoized) doesn't re-render unnecessarily. Parameters: (1) the callback to memoize, (2) a dependency array controlling when a new memoized version is created.

**Q: What does `useMemo` do, and what are its parameters?**
It memoizes the *result* of an expensive computation, recalculating only when a dependency changes. Parameters: (1) a function that performs the computation and returns a result, (2) a dependency array. It returns the memoized value itself (not a function).

**Q: What is `useRef` used for?**
Primarily for accessing/interacting with DOM elements directly, and for holding any mutable value that needs to persist across renders — unlike state, updating a ref does *not* trigger a re-render.

**Q: What are the Rules/Best Practices for using Hooks?**
Call Hooks only at the top level of a component (never inside conditionals/loops), call them only from React function components or custom hooks, and keep their call order consistent across renders.

**Q: What are Custom Hooks?**
Plain JavaScript functions (conventionally prefixed `use...`) that developers write to encapsulate and reuse stateful logic across components.

**Q: What are three scenarios where you'd use `useEffect`?**
Fetching data from an external API, managing subscriptions/event listeners, performing manual DOM manipulation, and setting up timers/intervals.

**Q: How do you conditionally run an effect?**
Put the `if`/`else` condition *inside* the effect callback itself — the hook call itself must never be conditional.

**Q: What problem do Hooks solve, and what's their advantage over class lifecycle methods?**
They let function components manage state, lifecycle-equivalent behavior, and side effects without classes — eliminating class boilerplate, `this`-binding headaches, and scattered lifecycle logic, in favor of more concise, colocated, readable code.

### Interview Q&A: Class Component Lifecycle Methods

*(The class-lifecycle-to-`useEffect` mapping table is covered above under "Hooks & State Architecture" — these questions cover the class-specific mechanics that table doesn't spell out.)*

**Q: What are the three component lifecycle phases?**
Mounting (the component is created and inserted into the DOM), Updating (the component re-renders in response to a props or state change), and Unmounting (the component is removed from the DOM).

**Q: What are the lifecycle methods in each phase?**

```text
Mounting                    Updating                       Unmounting
constructor()                getDerivedStateFromProps()    componentWillUnmount()
getDerivedStateFromProps()   shouldComponentUpdate()
render()                     render()
componentDidMount()          getSnapshotBeforeUpdate()
                              componentDidUpdate()
```

**Q: What is a constructor in a class component, and when do you use one?**
A special method invoked when a class instance is created — used to initialize `this.state` and perform any setup needed before the first render.

**Q: What is the role of the `super` keyword in a constructor?**
It calls the parent class's (`React.Component`) constructor, which is required so the parent's own initialization (notably wiring up `this.props`) runs correctly before your own constructor logic.

**Q: What does the `render()` method do?**
Returns the React elements (JSX) that should be rendered to the DOM. It's required on every class component.

**Q: How is state maintained in a class component?**
Two-step process: `this.setState()` updates the state, and `this.state` is read to render the current value in the DOM.

**Q: What does `componentDidMount()` do?**
Runs once, immediately after the component is first rendered into the DOM — the standard place for side effects like data fetching or setting up subscriptions.

**Q: What does `componentDidUpdate()` do?**
Runs after the component re-renders due to a props or state change — commonly used to re-fetch data in response to that change (guarded by a comparison check against the previous props/state, to avoid an infinite update loop).

**Q: What does `componentWillUnmount()` do?**
Runs just before the component is removed from the DOM — used for cleanup: removing event listeners, cancelling subscriptions/timers, or aborting in-flight requests.

**Q: How do you initialize state in a class component?**
Inside the constructor, e.g. `this.state = { count: 0 }`.

**Q: In which lifecycle phase does a component re-render?**
The Updating phase, triggered whenever its props or state change.

**Q: What happens if you don't define a constructor?**
React automatically supplies a default constructor that calls `super(props)` for you.

**Q: Why do we still need class components if functional components exist?**
Mainly for maintaining legacy code predating Hooks, supporting third-party libraries still written as class components, and working with existing lifecycle-method-based code.

**Q: What are the 5 main lifecycle methods, in order?**
`constructor()` (initialize state) → `render()` (return JSX) → `componentDidMount()` (post-mount side effects) → `componentDidUpdate()` (post-update side effects) → `componentWillUnmount()` (cleanup before removal).

### Interview Q&A: Controlled vs. Uncontrolled Forms

**Q: What is a controlled component?**
A form element (input, checkbox, etc.) whose value is driven by component state rather than by the DOM itself — its value is set from state, and an `onChange` handler updates that state on every change.

**Q: Controlled vs. uncontrolled — what's the difference?**

| Controlled | Uncontrolled |
|---|---|
| Value controlled by React state | Value lives in the DOM itself |
| Event handlers update state | No explicit state update; read via a ref |
| Re-renders on every change | Fewer re-renders |
| Standard/recommended practice | Useful in specific scenarios, less common |

**Q: What are the characteristics of a controlled component?**
State control (the form element's value lives in component state), event handling (`onChange` etc. fires on user interaction), state update (the handler writes the new value into state), and re-rendering (the component re-renders and the element reflects the updated state).

**Q: What are the advantages of controlled components?**
A single source of truth for form values; predictable, synchronized updates that make validation and dynamic rendering straightforward; and better overall maintainability — which is why they're the recommended default for React forms.

**Q: How do you handle multiple input fields in a controlled form?**
Maintain a state variable (or one state object with a field per key) for each input, and update the relevant one individually in each field's `onChange` handler.

**Q: How do you handle form validation in a controlled component?**
Validate input values before committing them to state, and conditionally render validation/error messages based on that state.

**Q: When are uncontrolled components advantageous?**
When integrating with non-React (third-party or legacy) code, or in scenarios where a fully state-controlled approach isn't practical.

### Interview Q&A: Code Splitting Basics

*(`React.lazy` + `Suspense` as a bundle-size lever is introduced above under "Rendering Model, JSX & Reconciliation" — these cover the mechanics and trade-offs in more depth.)*

**Q: How do you implement code splitting in React, in 3 steps?**
1. Use `React.lazy()` to lazily import a component. 2. Wrap it in `<Suspense>` to handle the loading state. 3. Make sure your build tool (Webpack/Vite) is configured for dynamic `import()`.

**Q: What is the role of `import()` in code splitting?**
It returns a Promise, enabling a module to be loaded dynamically/on demand instead of bundled upfront.

**Q: What is the purpose of the `fallback` prop on `<Suspense>`?**
It provides the loading UI shown while the lazily-imported component is still being fetched.

**Q: What are the pros and cons of code splitting?**

*Pros:* faster initial load (only ships what the current view needs); optimized bandwidth usage; improved browser caching (smaller, focused chunks); parallel chunk loading; easier long-term maintenance (more modular codebase).

*Cons:* added implementation complexity; dependency on specific build tooling/config; possibility of runtime errors from dynamic loading; more HTTP requests overall; a real learning curve for teams new to it.

**Q: Can you dynamically load CSS via code splitting?**
Yes — a dynamic `import()` can load a stylesheet on demand alongside its corresponding component.

**Q: How do you inspect and analyze the generated chunks in a React app?**
Tools like Webpack Bundle Analyzer visualize each chunk's size and composition.

### Interview Q&A: React Odds & Ends

*(Higher-Order Components are covered above under "Composition Patterns"; general performance-optimization levers under "Performance, Memoization & Concurrent Rendering" — these are the remaining standalone questions from this chapter.)*

**Q: What are 5 ways to style React components?**
Inline styles, CSS stylesheets, CSS Modules, global stylesheets, and CSS frameworks (e.g. Tailwind).

**Q: React vs. React Native — what's the difference?**

| React | React Native |
|---|---|
| A library | A framework |
| Builds web interfaces | Builds mobile apps |
| Runs in browsers | Runs on iOS/Android |
| Uses HTML & CSS | Uses native UI components (`View`, `Text`, ...) |
| Deployed as a web app | Deployed through app stores |

**Q: What is GraphQL, and how does it relate to React?**
A query language for APIs plus a runtime for executing those queries against existing data. React components commonly use GraphQL queries to fetch exactly the data they need for rendering.

**Q: What are the top 3 ways to manage state in React, and when do you use each?**
`useState` for simple, component-local state (lightweight, built in). The Context API to avoid prop drilling when sharing global-ish data across the tree. Redux for large, complex applications needing centralized, predictable state shared across many components.

**Q: How would you implement authentication in a React app?**
Client POSTs credentials (`{username, password}`) → server authenticates and creates a JWT → server returns the token → client stores it (e.g. `localStorage`) and attaches it to subsequent requests (typically an `Authorization` header) → server validates the token's signature on each request → server returns the requested data → client renders it.

**Q: What is the React Profiler used for?**
A built-in tool for measuring and analyzing a React application's rendering performance.

**Q: `fetch` vs. `axios` — what's the difference?**
`fetch` is built into the browser (no extra dependency) and returns Promises, which is enough for simple requests. `axios` is a third-party library that adds interceptors — useful for request/response logging, centralized auth handling, and richer error handling — worth reaching for once you need that interception layer.

**Q: What are the popular testing libraries for React?**
Jest, React Testing Library, Enzyme, and Cypress.

**Q: How can you optimize performance in a React app? (quick list)**
Memoize with `useMemo`/`useCallback`; use `React.Fragment` to avoid unnecessary wrapper DOM nodes; lazy-load with `React.lazy`; apply code splitting; and optimize/compress images and other static assets. *(See "Performance, Memoization & Concurrent Rendering" above for the deeper triage process.)*

**Q: What is Reactive Programming?**
A paradigm focused on reacting to changes and events in a declarative, asynchronous manner — declarative meaning you describe *what* you want (JSX is a declarative example), asynchronous meaning an action doesn't block other actions from proceeding.

**Q: In how many ways can you implement Reactive Programming in React?**
State & props, Hooks (`useState`/`useEffect`), event handling, the Context API, Redux, class lifecycle methods, `async`/`await`, and RxJS/Observables.

**Q: How do you pass data from a child component up to its parent?**
The parent passes a callback function down to the child as a prop; the child invokes that callback (optionally with data) to send information back up.

**Predictive Interview Questions (React):**
1. Walk me through what happens, step by step, from a `setState` call to pixels changing on screen — where does batching happen, and where does the diffing algorithm make its type-based bailout decision?
2. Your team has a dashboard where one Context (`AppState`) holds theme, auth, and 15 widgets' live data. Profiling shows every widget re-renders on every WebSocket tick. How do you re-architect this, and what would you replace Context with?
3. Tell me about a time you inherited a React app with a severe re-render performance problem. What was the root cause, how did you diagnose it (tools, not guesses), and what was the measurable impact of your fix on user-facing metrics?
4. You're asked to add tests to a legacy feature with no existing coverage, connected to both Redux and a Context provider, that fetches data on mount. Walk through your testing strategy — what do you test at which layer, and how do you handle the async data fetch and the Redux/Context dependencies?
5. Describe a time you had to choose between two "correct" architectural approaches with different long-term trade-offs — for example, `BrowserRouter` vs. `HashRouter` under a hosting constraint, or a Context refactor vs. adopting a new state library. How did you frame that decision for a non-technical stakeholder who just wanted to know "why is this taking longer than expected"?

**Executive Summary Cheat Sheet (React):** React is a view library, not a framework — its architecture (Virtual DOM diffing, unidirectional data flow, and now Server Components) trades ecosystem flexibility for the discipline of choosing your own router, state layer, and data-fetching strategy deliberately. At senior level, the recurring judgment calls are Context-vs-dedicated-state-library based on update frequency, manual-memoization-vs-Compiler-reliance based on profiling evidence, RSC-vs-Client-Component boundaries based on where interactivity actually lives, and — just as often tested — which layer of the testing pyramid and which composition pattern a given piece of code actually calls for.

## Redux

### Core Architecture & Unidirectional Data Flow
- Redux's three principles — single source of truth, read-only state (changes only via dispatched actions), and changes via pure reducer functions — exist to make state mutation traceable and time-travel-debuggable, not because "pure functions are nice."
- ⚖️ Redux vs. React local state: Redux centralizes state outside the component tree at the cost of setup ceremony (actions, reducers, dispatch) — worth it once "prop drilling through unrelated components" or "need for time-travel debugging / middleware" becomes real; overkill for a form's local input state.
- Reducers must be pure because Redux detects change via reference equality, not deep comparison — mutating state in place leaves the object reference unchanged, so Redux (and connected components) never know anything happened.
- Middleware sits between dispatch and the reducer as an interception pipeline — Thunk for simple async, Saga (generator-based) for complex concurrent async workflows, custom logging middleware for observability.
- The Provider/useSelector/useDispatch trio is the React-Redux binding: Provider exposes the store via Context, useSelector subscribes a component to a slice of state, useDispatch sends actions into the pipeline.
- 📉 Selectors without memoization re-run their transformation logic on every dispatched action regardless of relevance — `createSelector` (Reselect) caches by reference-equal inputs, which is why using it is non-negotiable for any selector that filters/maps/derives data.
- State normalization (entities keyed by ID + an ids array) turns nested API responses into a flat, database-like shape — this is what makes single-item updates O(1) instead of requiring a deep array scan.

```text
Unidirectional Redux loop:
User Action ➔ dispatch(action) ➔ Reducer (pure fn) ➔ new Store state ➔ connected components re-render
```

**Senior Perspective:**
- Redux's real value isn't "global state," it's a *predictable mutation contract* — time-travel debugging and deterministic replay are why regulated/enterprise teams still choose it over ad-hoc state libraries.
- The reference-equality mental model explains 90% of "my component didn't update" bugs — a senior engineer diagnoses this in seconds, not by adding console.logs everywhere.

### Redux Toolkit & the Modern Ecosystem
- Redux Toolkit (RTK) is the answer to three historic Redux complaints — excessive boilerplate, complicated setup, and easy-to-cause mutation bugs — via `configureStore` (auto-wires DevTools + Thunk + serializability/immutability checks) and `createSlice` (generates action creators + reducer in one block).
- Immer (bundled in RTK) lets you write `state.items.push(x)`-style "mutating" code inside a `createSlice` reducer; Immer intercepts it via a draft state and produces a safe immutable copy underneath — this is the mechanism that makes RTK reducers look imperative while staying pure.
- `createAsyncThunk` auto-generates pending/fulfilled/rejected action creators for a Promise-returning function, which a slice's `extraReducers` consumes to drive loading/error/success UI without hand-rolled lifecycle plumbing.
- ⚖️ RTK Query vs. TanStack Query/SWR: RTK Query is deeply integrated with the Redux store (unifies UI state and server state under one architecture, no separate cache layer) but couples you to Redux; TanStack Query/SWR are Redux-agnostic and lighter for apps that don't otherwise need Redux — choose based on whether Redux is already the app's backbone.
- RTK Query's tag-based cache invalidation (a mutation declares which tags it invalidates; matching query endpoints auto-refetch) is the mechanism that keeps five screens showing the same entity in sync without manual cache busting.
- `createEntityAdapter` auto-generates the entities+ids normalized shape plus CRUD reducers (`addOne`, `upsertMany`, `removeOne`) and memoized selectors (`selectAll`, `selectById`) — it's the productized version of manual normalization.
- Typed hooks (`useAppSelector`/`useAppDispatch` bound via `withTypes<RootState>()`) centralize TypeScript inference once instead of re-declaring state types in every component.

```text
RTK Query cache invalidation:
Mutation (addTask) → declares invalidatesTags: ['Tasks']
   → RTK Query detects 'Tasks' query is stale → auto-refetches → all subscribed components re-render with fresh data
```

**Senior Perspective:**
- RTK isn't "easier Redux," it's the officially sanctioned architecture — recommending vanilla Redux over RTK in 2026 is itself a code-review flag.
- The RTK-Query-vs-TanStack-Query decision is really a question of "is Redux the backbone of this app, or is server-state caching a standalone concern" — that framing is what interviewers are listening for.

### Performance, Normalization & State Architecture at Scale
- Server State (async, cacheable, goes stale) vs. Client State (synchronous, ephemeral, local) is the same split React needs — Redux/RTK Query own the former, `useState`/local slices own the latter; mixing them (storing derived/calculated totals in the store) causes sync bugs.
- ⚖️ Normalized vs. denormalized state: denormalized trees cause cascading re-renders because a leaf change alters every ancestor's reference; normalized (flat entities+ids) gives O(1) targeted updates at the cost of a flattening pass on ingest — for any list-heavy app, normalized wins.
- Feature-sliced folder architecture (`src/features/billing/{slice,components,hooks}`) scoped with RTK 2.0's `combineSlices` + `.inject()` lets you lazy-load state modules per-route, keeping a 200+-screen enterprise app's initial bundle lean.
- Cross-slice communication (e.g., logout clearing cart + UI state) is handled via `extraReducers` listening for another slice's action type — not by dispatching five separate actions from the UI component.
- Listener middleware (`createListenerMiddleware`) replaces hand-rolled debounce/throttle/cancellation logic for reactive side effects — WebSocket ingestion, autosave, rate-limited search are the canonical use cases.
- Optimistic updates with rollback use `onQueryStarted` + `dispatch(api.util.updateQueryData(...))` to mutate the cache instantly, keeping the returned `.undo()` handle inside a try/catch to reverse on server failure.
- Redux in SSR/Next.js requires a per-request store factory (not a global singleton) to avoid state bleeding across concurrent user requests, with client-side reducers listening for a hydration action to merge server state cleanly.

```text
Normalized state shape:
state.users = { entities: { '1': {...}, '2': {...} }, ids: ['1','2'] }
state.posts = { entities: { 'p1': { id:'p1', userId:'1', ... } }, ids: ['p1'] }
```

**Senior Perspective:**
- "Store the calculated cart total in Redux" is the classic anti-pattern trap — derived values belong in a memoized selector, not in mutable state, or they will drift out of sync with their inputs.
- Feature-sliced + lazy-injected reducers is the architecture question a staff-level Redux interview is actually probing — it signals whether a candidate has operated Redux past "todo app" scale.

### When to Avoid Redux & Testing Strategy
- ⚖️ Avoid Redux entirely for lightweight apps, mostly-server-state apps (TanStack Query/SWR cover caching/sync with zero boilerplate), or simple global config (Context/Zustand) — reaching for Redux by default, rather than by need, is itself the anti-pattern senior engineers are expected to push back on.
- Comparison matrix: Redux+RTK Query wins for enterprise-scale normalization/caching/debugging needs; Zustand for minimal-boilerplate medium apps; Jotai for atomic, independently-updating UI state (canvases, editors); Context for low-frequency global config.
- Testing pyramid: unit-test slice reducers (pure functions — pass state + action, assert output), use MSW to simulate async thunk/RTK Query lifecycle stages, and integration-test connected components via a `renderWithProviders` helper wrapping a real (mock-data-seeded) `<Provider>`.

**Senior Perspective:**
- Knowing when *not* to use Redux is a stronger signal of seniority than knowing how to configure it — over-centralizing UI-only state (modal open/closed) into a global store is a common mid-level mistake.

### Interview Q&A: Redux Mechanics — Actions, Store, Reducer & `connect()`

*(Redux's three core principles, the Provider/useSelector/useDispatch binding, and state normalization are covered above under "Core Architecture & Unidirectional Data Flow" — these cover the classic mechanics and the `connect()`-based pattern you'll still meet in older codebases.)*

**Q: What is the role of Redux in a React app?**
Redux is a state-management library providing one centralized store that holds an application's entire state; components dispatch actions, and reducers update that store in a predictable, traceable way.

**Q: When would you reach for plain Hooks vs. Redux?**

| Use Hooks when | Use Redux when |
|---|---|
| App is small/medium (~5–50 components) | App is big/complex (50+ components) |
| State management is simple | Global state is genuinely complex |
| State is specific to one component | State must be shared across many components |

**Q: What is the flow of data in a React app using Redux?**
A component interaction dispatches an Action (built by an Action Creator) → the Reducer receives `(previousState, action)` → it computes and returns the new state → the Store holds that current state → subscribed components re-render from it.

**Q: What are Action Creators?**
Functions that create and return action objects.

**Q: What's the difference between an Action Creator, an Action Object, and an Action Type?**
An Action Creator is the *function* that builds and returns an action. The Action Object is the plain JS object it returns (typically `{ type, payload }`). The Action Type is the string constant identifying what kind of action it is.

**Q: Walk through the classic `connect()`-based React-Redux component structure.**
1. Import `connect` and your action creators. 2. Define the functional component that renders the UI. 3. Define a function that dispatches an action to the reducer via the store. 4. Define a function (`mapStateToProps`) that reads the needed state from the store into props. 5. Wire the component together with both functions via `connect(mapStateToProps, mapDispatchToProps)(Component)`.

**Q: What is the role of the Store?**
A centralized place holding the state for every component in the app, and the object through which state updates (via reducers) actually happen.

**Q: What is the role of a Reducer?**
A pure function that takes the previous state and an action as arguments and returns the new state of the application.

**Q: What is the Provider component, and how do components get state from the store?**
`<Provider>` (from `react-redux`) makes the Redux store available to every connected descendant component via Context, without it being passed down manually.

**Q: What is the role of the `connect()` function?**
It wires a React component up to the Redux store, injecting selected state and dispatch-bound action creators as props.

**Q: What are the 4 important files in a typical React-Redux project?**

```text
src/
├── actions.js          # action creators
├── reducer.js           # (previousState, action) → newState
├── store.js             # holds current state, exported to components
└── CounterComponent.js  # connected component: reads state, dispatches actions
```

As an app grows, this typically splits into `actions/`, `reducers/`, `store/`, and `components/` folders, one file per feature/domain.

**Q: Typical properties of an Action object?**
`type` (a string describing what action is being performed) and `payload` (the data the reducer needs, often sourced from an API response).

**Q: `mapDispatchToProps` vs. `mapStateToProps`?**
`mapDispatchToProps` wires action-dispatching functions into props (sends actions to the store via the reducer). `mapStateToProps` reads state from the store into props.

**Q: What does "Unidirectional Data Flow" mean in Redux?**
Data always moves in one consistent direction — component interaction → dispatch → reducer → store → component re-render — which is what makes state changes traceable and predictable.

**Q: How does Redux handle communication between components?**
Components never talk to each other directly — every component dispatches to, and reads from, the same centralized store, which mediates all cross-component communication.

**Q: What is the `payload` property?**
The part of an action (alongside `type`) that carries the actual data the reducer needs in order to compute the new state.

**Q: Explain immutability in the context of Redux.**
Once created, state is never modified directly — to make a change you dispatch an action, and the reducer returns a brand-new state object rather than mutating the existing one in place.

### Interview Q&A: Redux Trade-offs, Thunk, Middleware & Flux

*(Redux's core principles are covered above under "Core Architecture & Unidirectional Data Flow"; the RTK-Query-vs-alternatives decision tree is covered under "When to Avoid Redux & Testing Strategy" — these cover the classic pros/cons list and vanilla Thunk/middleware mechanics.)*

**Q: What are 5 benefits of using Redux?**
Predictability & centralization (one predictable source of truth); maintainability at scale (structured, scalable state management); debuggability (powerful DevTools for tracing state changes); interoperability (works across various JS frameworks); and a large community/ecosystem.

**Q: Local component state vs. Redux state — what's the difference?**

| Local Component State | Redux State |
|---|---|
| Scoped to the component that defines it | Global, accessible across components |
| Managed internally | Managed externally by the store |
| Simpler to set up and test | More performant/structured at large scale, but more complex |

**Q: What are the challenges/disadvantages of using Redux?**
Boilerplate code (actions, reducers, store wiring); a real learning curve; growing verbosity/complexity as a project scales; unnecessary overhead for small projects; the temptation to over-globalize state that should stay local; and extra integration effort when combining Redux with non-React libraries.

**Q: Regular action creator vs. Thunk action creator — what's the difference?**
A regular action creator returns a plain object with a `type` property. A Thunk action creator instead returns *a function* — that returned function is what actually gets dispatched, which is what lets it perform async work (like an API call) before deciding which action to eventually dispatch.

**Q: How do you handle asynchronous operations and side effects in Redux?**
Via middleware, typically Redux Thunk action creators that perform the async work and dispatch the resulting action once it resolves.

**Q: How does error handling work in Redux?**
Via `try`/`catch` blocks placed in action creators, middleware, and/or reducers as appropriate.

**Q: Flux vs. Redux — what's the difference?**
Flux is an architectural *pattern* — a set of principles for organizing unidirectional state management. Redux is a specific *library* that implements the Flux pattern.

**Predictive Interview Questions (Redux):**
1. Explain exactly why Redux requires reducers to return a new object rather than mutate state in place — what internal mechanism breaks if you don't, and how does Immer let you write mutating-looking code safely anyway?
2. You have five different screens all displaying the same "current user's projects" list, each fetching independently today. How would you redesign this with RTK Query to eliminate redundant requests and keep them all in sync after a mutation?
3. Tell me about a time your team had to decide between Redux and a lighter alternative (Context, Zustand, TanStack Query) for a new feature. What factors drove the decision, and would you make the same call again given what you learned in production?

**Executive Summary Cheat Sheet (Redux):** Redux enforces a strict unidirectional contract — actions in, pure reducers out, reference-equality-driven re-renders — which buys predictability and time-travel debugging at the cost of setup ceremony that Redux Toolkit now eliminates almost entirely. At senior level, the real skill is architectural triage: normalizing state for scale, separating server state (RTK Query) from client state, and knowing when Redux is the wrong tool versus reaching for it by habit.

## Angular

### Architecture Renaissance: Components, Modules & Data Binding
- 🏗️ Angular v17 ("the Renaissance") is the inflection point: new control-flow syntax (`@if`/`@for`/`@switch`), the Signals reactivity system, and standalone components (no NgModule requirement) collectively repositioned Angular from "heavy enterprise framework" to a framework competitive on developer ergonomics with React/Vue.
- A component is three co-located files (TypeScript "brain," HTML "skeleton," CSS "skin") wired together by the `@Component` decorator — decorators (`@Component`, `@Injectable`, `@Input()`, `@Output()`) are Angular's metadata layer that tells the compiler what a class *is*, not just what it does.
- Four data-binding types cover the full sync surface: interpolation (`{{ }}`, code→HTML text, one-way), property binding (`[prop]`, code→element property), event binding (`(event)`, user action→code), two-way binding (`[(ngModel)]`, continuous sync — de-sugars to simultaneous `[value]` + `(input)`).
- ⚖️ NgModules vs. Standalone Components: NgModules group related pieces and their dependencies explicitly but add ceremony; standalone components (default since v14-17) let each component list its own imports, improving tree-shaking and removing the "which module do I register this in" tax — legacy enterprise codebases still carry NgModules, new code shouldn't.
- View Encapsulation has three modes — Emulated (default, unique attribute-based simulated boundary), None (fully global CSS, easy leakage), ShadowDom (native browser-enforced hard boundary) — the trade-off is isolation strength vs. simplicity/performance.
- Directives split into three categories: Components (directives with a template), Structural (`*ngIf`/`*ngFor`, or the modern `@if`/`@for`, which add/remove DOM nodes), Attribute (`ngClass`/`ngStyle`, which change appearance/behavior without adding/removing).
- 📉 The new built-in `@for` block is measurably faster than `*ngFor` because it's compiled directly into the engine rather than processed as an external structural directive — up to 90% faster on large-list updates, and the `track` property (mandatory) is what lets Angular slide existing DOM nodes instead of destroying/rebuilding the whole list on reorder.

```text
Data binding directions:
{{ value }}         Code ──────────────➔ HTML   (interpolation)
[disabled]="cond"   Code ──────────────➔ Element property
(click)="fn()"      User action ───────➔ Code
[(ngModel)]="val"   Code ⇄ Element (continuous two-way loop)
```

**Senior Perspective:**
- Angular's opinionated, batteries-included model (router, forms, DI, HTTP client all built-in) trades the "decision fatigue" React teams accept for architectural consistency across large, multi-team enterprise codebases — that trade-off is *the* Angular-vs-React interview framing.
- Standalone components collapsing the NgModule requirement is the single biggest DX shift of the Renaissance — a senior engineer evaluating a legacy Angular codebase should treat heavy NgModule usage as a migration-debt signal, not a stylistic choice.

### Dependency Injection & Services
- Dependency Injection means a class *requests* its collaborators (services) from Angular's injector rather than constructing them itself — this is what makes services swappable for testing (mock injection) and shareable as singletons without manual wiring.
- The Hierarchical Injection System mirrors the component tree: a service request walks up from the component's own injector to parent, to root, until found — `providedIn: 'root'` gives one app-wide singleton (tree-shakeable if unused), while component-level `providers` create a fresh instance per component instance (five uses = five isolated copies).
- ⚖️ `providedIn: 'root'` vs. module-level providers: root-provided services are tree-shaken out of the bundle if never injected; module-level providers are not tree-shakeable and stay in the bundle even if unused — root is the default correct choice in 2026, module-level is a legacy pattern.
- The modern `inject()` function replaces constructor injection for field initializers and factory functions, reducing constructor boilerplate and simplifying inheritance — constructor injection still works but is increasingly the "old way."
- Injection Tokens (`InjectionToken`) exist because TypeScript interfaces vanish at compile time — you can't inject "by type" for non-class values (config objects, strings, browser APIs), so a token acts as a runtime-durable lookup key.
- Provider "recipes" — `useClass` (new instance), `useValue` (static value), `useExisting` (alias to another provider), `useFactory` (computed, e.g. role-based service selection) — redirect what a token resolves to, the mechanism behind swapping in mocks for tests.
- Resolution Modifiers (`@Optional`, `@Self`, `@SkipSelf`, `@Host`) fine-tune *where* in the injector tree a lookup starts/stops — used for building self-contained, boundary-respecting component libraries.
- `providers` vs. `viewProviders`: `providers` extends to projected `<ng-content>` content; `viewProviders` is restricted to the component's own template only — a privacy mechanism for library authors.
- Environment Providers (`provideRouter()`, `provideHttpClient()` in `app.config.ts`) are the standalone-era replacement for module-level app-wide service registration.

```text
Hierarchical injector lookup:
Component's own injector → not found → Parent component injector → not found → Root injector (singleton)
Component-level `providers: [MyService]` short-circuits this: creates a private instance, invisible to siblings.
```

**Senior Perspective:**
- DI is Angular's biggest structural advantage over React for enterprise teams — it makes testability and swappability first-class instead of something bolted on with mocking libraries.
- Choosing root-provided vs. component-scoped services is an architecture decision about *identity*, not just convenience — get it wrong and you either leak state across unrelated component instances or duplicate state that should be shared.

### RxJS & Reactive Streams
- RxJS treats async data as a continuous stream rather than a single value — Angular uses it pervasively (HTTP returns Observables, forms stream keystrokes, Router emits navigation events).
- ⚖️ Observable vs. Promise: Promises are eager (start immediately) and single-delivery; Observables are lazy (don't run until subscribed) and multi-delivery, with built-in cancellation (`unsubscribe()`) that Promises lack — Observables' operator ecosystem (map/filter/switchMap/etc.) is the other major differentiator.
- Subject types solve different "replay" needs: `BehaviorSubject` (stores/replays the latest value to new subscribers — default for state), `ReplaySubject` (replays N historical values), `AsyncSubject` (emits only the final value, only on completion).
- ⚖️ Observable vs. Subject: an Observable is unicast (each subscriber triggers its own independent execution — two subscribers to an HTTP call fire two network requests); a Subject is multicast (all subscribers share one execution) — Subjects are right for event buses/global state, not for wrapping independent HTTP calls.
- Cold vs. Hot Observables: Cold doesn't produce data until subscribed and gives each subscriber an independent replay from the start (like on-demand video); Hot produces data regardless of subscribers and late joiners miss earlier emissions (like live radio) — mouse movements and stock tickers are inherently hot.
- Higher-order mapping operators resolve "stream triggers another stream" timing: `switchMap` cancels the previous inner stream on a new emission (search-as-you-type), `mergeMap` runs all inner streams concurrently (independent saves), `concatMap` queues them strictly in order (sequential steps), `exhaustMap` ignores new triggers until the current one finishes (login button — prevents double-submit).
- Error handling operators (`catchError` to intercept and fall back gracefully, `retry(n)` to auto-resubscribe on transient failure) keep a single failure from permanently killing a stream.
- `tap` (side effect, passes data through unchanged) vs. `map` (transforms the data) is a common confusion point — `tap` is for logging/spinners, never for altering the emitted value.
- `forkJoin` (waits for all streams to complete, emits once — like `Promise.all`) vs. `combineLatest` (emits as soon as all streams have emitted once, then re-emits on any subsequent change — ideal for reactive filter UIs).
- `takeUntil` (classic cleanup via a "destroy" notifier) is superseded by `takeUntilDestroyed()` (Angular 16+), which auto-detects component/service destruction and removes the need for manual notifier + `ngOnDestroy` boilerplate.
- 📉 Backpressure (producer faster than consumer — e.g., 1000 msgs/sec from a server vs. 60fps render budget) is handled with "lossy" operators (`debounceTime`, `throttleTime`, `sampleTime`) that intentionally discard data to prevent memory blow-up and UI jank.
- `share()`/`shareReplay(1)` convert a Cold Observable into a Hot, multicast one — `shareReplay(1)` is the standard caching pattern so late-joining components get the last emitted value instantly instead of re-triggering the source.

```text
switchMap (search box):  keystroke1 → request1 (cancelled)
                          keystroke2 → request2 (cancelled)
                          keystroke3 → request3 (completes, only this result renders)
```

**Senior Perspective:**
- Picking the right higher-order mapping operator (switchMap vs. mergeMap vs. concatMap vs. exhaustMap) is the single most-tested RxJS judgment call in interviews because getting it wrong causes real production bugs (race conditions, duplicate submissions, out-of-order UI updates).
- `takeUntilDestroyed()` replacing manual `Subject`-based cleanup is the kind of ergonomic win a senior engineer should be actively migrating legacy code toward — it eliminates an entire category of memory-leak bugs by construction.

### Signals: The New Reactivity Model
- 🏗️ Signals are Angular's fine-grained reactivity primitive: a Signal knows exactly which template bindings read it and pushes updates only to those, replacing Zone.js's "re-check everything on every browser event" model with surgical, targeted DOM updates.
- Three core primitives: `signal()` (writable container, `.set()`/`.update()`), `computed()` (read-only, lazily-evaluated and cached — only recalculates when a dependency actually changes), `effect()` (runs a side effect whenever its read signals change; reserved for external-world tasks like logging or localStorage, not for derived data — that's `computed()`'s job).
- Signals are "glitch-free" by design: a Push/Pull algorithm notifies dependents that a value is "dirty" without immediately recomputing, then calculates in the correct order only when a value is actually pulled — this solves the classic "diamond problem" where naive reactive systems double-fire and briefly show stale intermediate state.
- `linkedSignal()` (2025/2026) is a writable signal that auto-resets to a new default whenever its source signal changes, while still allowing manual overwrites — purpose-built for patterns like "quantity resets to 1 when the selected product changes, but the user can still type 5."
- `resource()` is a signal-based async data-fetching primitive that auto-manages the full request lifecycle (fetch-on-request-change, `.isLoading`, `.error`) — the signal-world answer to what `useEffect` + manual loading state used to require.
- Interop functions bridge the two reactivity worlds: `toSignal()` (Observable → Signal, auto-unsubscribes, for showing async data in templates) and `toObservable()` (Signal → Observable, for applying RxJS timing operators like debounce to a signal-driven value) — Signals own "state," RxJS still owns "timing and events."
- `untracked()` reads a signal inside an `effect()`/`computed()` without creating a dependency on it — necessary when you need a value's current snapshot without re-triggering on every change to *that* signal, only on the signal you actually care about.
- Signal Inputs (`input()`) and Model Inputs (`model()`) replace `@Input()`/`@Output()` pairs with natively-reactive, type-safe alternatives — `model()` collapses two-way binding into one primitive instead of manually wiring an EventEmitter.
- Signal Queries (`viewChild()`, `contentChild()`) replace `@ViewChild`/`@ContentChild` decorators and return Signals instead of plain (often-`undefined`-until-a-lifecycle-hook) values, removing entire classes of timing bugs.

```text
Fine-grained reactivity:
signal(count) changes → only DOM nodes subscribed to {{ count() }} re-render
                       → sibling nodes reading unrelated signals are untouched
(vs. Zone.js: any browser event → re-check the entire component tree)
```

**Senior Perspective:**
- Signals vs. RxJS isn't either/or — the professional pattern is Signals for "what does the UI currently show" and RxJS for "how do I control timing/cancellation of async events," bridged by `toSignal`/`toObservable`.
- `computed()` for derivation and `effect()` only for genuine side effects is the discipline that keeps signal-based Angular apps predictable — using `effect()` to "calculate" a value is the new-Angular equivalent of the old ngDoCheck-abuse anti-pattern.

### Lifecycle, Change Detection & Performance
- Lifecycle hooks run in a fixed order (ngOnChanges → ngOnInit → ngDoCheck → ngAfterContentInit → ngAfterContentChecked → ngAfterViewInit → ngAfterViewChecked → ngOnDestroy) — `ngOnInit` is for initialization logic (API calls, dependent on `@Input()` data being ready), the constructor is for DI only.
- ⚖️ `ngDoCheck` runs on *every* change-detection cycle (potentially hundreds of times per second) — any non-trivial logic inside it directly causes UI jank; Signals/Observables are the modern replacement because they only fire on actual data changes, not on every browser event.
- `ChangeDetectionStrategy.OnPush` tells Angular to skip checking a component unless its `@Input()`s change by reference, an internal event fires, or a signal it reads emits — combined with Signals, this is the "Golden Rule" 2026 performance pattern, because Signals make OnPush's reference-check requirement automatic rather than a manual discipline (immutable updates everywhere).
- `afterRender`/`afterNextRender` hooks replace `ngAfterViewInit` for DOM manipulation because they fire only in the actual browser (never during SSR, avoiding "window is not defined" crashes) and only after the browser has genuinely finished painting (avoiding `ExpressionChangedAfterItHasBeenCheckedError`).
- Zoneless Angular removes Zone.js entirely, relying solely on Signals to know what changed — this cuts ~13-15KB from the initial bundle and eliminates the "check the whole app on every click/timer" overhead, materially raising sustained FPS on data-heavy or mobile apps.
- 📉 Core Web Vitals optimization maps directly to Angular features: LCP via `NgOptimizedImage` (priority loading, correct srcset, layout-shift prevention) + SSR; INP via going Zoneless (removes framework-induced input delay); CLS via explicit image dimensions and `@defer` placeholders.

```text
OnPush + Signals (2026 golden rule):
Signal changes → Angular knows exactly which OnPush component subtree depends on it
             → only that subtree is checked, not the whole app
```

**Senior Perspective:**
- `ngDoCheck` abuse and forgetting OnPush are the two most common Angular performance code-smells a senior reviewer flags — both stem from not understanding *why* Angular's default change detection is expensive in the first place.
- The migration path (Standalone → Signals → OnPush → Zoneless) is a staged de-risking strategy, not a big-bang rewrite — knowing this sequence is what interviewers are testing when they ask "how would you modernize a legacy NgModule app."

### SSR, Hydration & Rendering Strategies
- SSR (Angular Universal) renders a ready-to-view HTML page on the server before sending it, trading a blank-screen-while-JS-downloads experience (CSR) for immediate visible content — the two wins are SEO (crawlers see finished HTML) and perceived speed on slow devices.
- Hydration "waters" the dry server-rendered HTML by attaching event listeners and Signal/state logic in the browser — a Hydration Mismatch error occurs when server-rendered and client-calculated initial state disagree (e.g., a timestamp that ticked between render and hydration).
- Incremental (Partial) Hydration hydrates page regions independently instead of all-at-once, avoiding the "page is visible but frozen for several seconds" problem on large SSR pages.
- Event Replay buffers user interactions (like a click) that happen before hydration completes and replays them once the relevant logic is ready — removes the "dead button" frustration common on slow-loading SSR sites.
- ⚖️ SSG vs. SSR vs. CSR: SSG pre-renders to static files at build time (fastest, cheapest, best for content identical for every visitor — docs, blogs); SSR renders per-request on a live server (freshest data, but server cost and latency per request); CSR ships a blank shell and builds client-side (best for private, highly-interactive dashboards that don't need SEO) — Route-level Render Modes let you mix all three per-URL in one app.
- `@defer` (Deferrable Views) lazy-loads a template chunk and its component based on a trigger (`on idle`, `on viewport`, `on hover`, `on interaction`, `on timer(ms)`, `when <signal>`), with `@placeholder`/`@loading`/`@error` sub-blocks managing the UX during each phase — Angular's answer to code-splitting below the route level.
- `isPlatformBrowser`/`isPlatformServer` (via injected `PLATFORM_ID`) guard browser-only code (localStorage, `window`) so the same component code runs safely on both the server render pass and the client hydration pass.

```text
Route-level render mode mixing:
/           → SSG (static marketing page, loads instantly from CDN)
/products/* → SSR (fresh data per request, SEO-critical)
/settings   → CSR (private, no SEO need, full client interactivity)
```

**Senior Perspective:**
- The Hydration Mismatch error is the Angular SSR bug every senior engineer has debugged at least once — the root cause is almost always non-deterministic initial state (Date.now(), random IDs, locale-dependent formatting) differing between server and client.
- Route-level render mode mixing (rather than "the whole app is SSR" or "the whole app is CSR") is the 2026-standard architectural answer to "how do you balance SEO, speed, and interactivity" — a single global rendering choice is now considered a legacy constraint, not a decision.

### Forms, Routing & Security
- ⚖️ Reactive Forms vs. Template-driven Forms: Reactive Forms are code-first (structure/validation defined in TypeScript, testable, scales to complex enterprise forms) at the cost of more setup; Template-driven Forms are HTML-first (`ngModel`-based, fast to write) but harder to test and messier as complexity grows — Reactive Forms is the standard for professional 2026 work.
- Control Value Accessor (CVA) is the interface (`writeValue`, `registerOnChange`, `registerOnTouched`, `setDisabledState`) that lets a fully custom component (a star rating, a signature pad) plug into `formControlName`/`[(ngModel)]` exactly like a native `<input>`.
- Route Guards intercept navigation: `CanActivate` (can the user enter?), `CanDeactivate` (can the user leave — e.g., unsaved-changes confirmation), `Resolve` (fetch data before the route renders, avoiding a blank-then-populate flash) — Functional Guards (using `inject()`) have replaced Class-based Guards as the lighter, more tree-shakeable modern pattern.
- The Interceptor pattern is HttpClient middleware for every outgoing request/incoming response in one place — auth token attachment, global 401 handling/logout, loading spinners, and request-timing logging are the four canonical uses.
- 🏗️ Angular's built-in XSS protection sanitizes all interpolated values by default (stripping `<script>` tags etc. from `{{ value }}`), and CSRF protection is a built-in cookie-to-header mechanism (`XSRF-TOKEN` cookie mirrored into an `X-XSRF-TOKEN` header) — both are "on by default," a structural advantage enterprise teams cite over hand-rolling this in less opinionated frameworks.

```text
Interceptor pipeline (single request):
Component → HttpClient.get() → AuthInterceptor (attach token) → LoggingInterceptor (start timer)
   → [Network] → ErrorInterceptor (catch 401 → logout) → LoggingInterceptor (log duration) → Component
```

**Senior Perspective:**
- Angular baking XSS/CSRF protection into the framework by default (vs. React/Vue leaving it to userland libraries) is a genuine architectural differentiator worth raising in any "why Angular for this project" conversation, especially for regulated industries.
- Functional Guards + `inject()` replacing Class-based Guards mirrors the same "de-ceremony" trend as standalone components and Signal Inputs — recognizing this pattern across Angular's evolution signals someone who's tracked the framework's direction, not just memorized its API surface at one point in time.

### Migration Strategy: Legacy NgModule to Zoneless/Signals
- 📉 The proven, staged roadmap for de-risking a large legacy migration: (1) Standalone migration via CLI schematic, removing NgModule requirements; (2) introduce Signals — replace `@Input()` with `input()`, local state with `signal()`, in the highest-churn components first; (3) apply `ChangeDetectionStrategy.OnPush` broadly, now safe because Signals guarantee reference-stable updates; (4) go Zoneless (`provideExperimentalZonelessChangeDetection()`) once most of the app is signal-driven.
- This is explicitly an "evolution, not revolution" — Standalone and NgModule-based code coexist in the same project during migration, letting a team keep shipping features while modernizing incrementally rather than freezing the codebase for a rewrite.

**Senior Perspective:**
- Every staff-level Angular interview eventually asks some version of "how do you migrate a legacy app" — the answer that signals seniority is the staged sequence above, explicitly justified by *why* each step de-risks the next (Signals before OnPush, OnPush before Zoneless), not just "rewrite it."

**Predictive Interview Questions (Angular):**
1. Walk me through exactly why `ngDoCheck` is dangerous for performance, and contrast it with how Signals solve the same "detect changes I care about" problem without the cost.
2. Your team is migrating a 5-year-old NgModule-based Angular app to Signals and eventually Zoneless. What's your staged migration order, and why does Signals have to come before OnPush, and OnPush before Zoneless — what breaks if you reorder that sequence?
3. Tell me about a production incident involving Angular's change detection — either a performance cliff or a subtle bug (like ExpressionChangedAfterItHasBeenCheckedError). How did you diagnose the root cause, and what architectural change prevented recurrence?

**Executive Summary Cheat Sheet (Angular):** Angular is deliberately opinionated — DI, routing, forms, and HTTP are built-in and standardized — trading React's stack-your-own flexibility for enterprise-grade consistency, and the 2026 "Renaissance" (Signals, Zoneless, standalone components, new control flow) has shed its old "heavy framework" reputation without abandoning that architectural discipline. At senior level, the recurring judgment calls are OnPush+Signals for fine-grained change detection, RxJS-vs-Signals based on whether you need timing/cancellation or just reactive state, and a staged (never big-bang) migration path from legacy NgModule/Zone.js architectures.

## Next.js

### Routing Architecture: App Router & File-System Conventions
- 🏗️ The App Router (Next.js 13+) is built on React Server Components by default — components stay server-side unless explicitly marked `"use client"`, which is the structural reason App Router apps ship less JavaScript than the legacy Pages Router by default.
- ⚖️ `layout.js` vs. `template.js`: layouts persist across sibling navigations (state like a search input survives) — ideal for headers/sidebars; templates re-mount fresh on every navigation (state resets) — use only when you deliberately want enter/exit animations or a reset-on-navigate form.
- Parallel Routes (`@slot` folders) render multiple independent page trees in one layout simultaneously, each with its own loading/error boundary — the standard pattern for dashboards where a failure or slow load in one widget shouldn't block the rest of the page.
- Intercepting Routes (`(.)folder`) load a route inside the current layout as a modal overlay while keeping the underlying page visible — the Instagram-photo-modal pattern — but a hard refresh or shared link still resolves to the full standalone page, giving both an app-like UX and a shareable URL for free.
- Route Groups (`(folder)`) organize files without affecting the URL and are the mechanism for Multiple Root Layouts (e.g., a marketing section with a hero header vs. a shop section with a simple navbar, each with its own `layout.js`).
- Dynamic segments (`[id]`), catch-all (`[...slug]`, requires at least one segment), and optional catch-all (`[[...slug]]`, matches zero or more — including the bare parent route) cover progressively broader URL-matching needs, commonly for CMS/docs sites with unpredictable depth.
- `loading.js` wraps a route in React Suspense automatically, showing instant skeleton UI without manual "if loading" branches scattered through components; `not-found.js` (triggered declaratively via `notFound()`) and `error.js` (must be a Client Component — error recovery requires interactivity for the "Try Again" button) provide route-scoped boundaries, while `global-error.js` is the last-resort handler for failures in the Root Layout itself (must define its own `<html>`/`<body>`).
- Link Prefetching downloads a linked page's code as soon as the `<Link>` enters the viewport, making clicks feel instant — `prefetch={false}` opts specific links (logout buttons, rarely-visited heavy pages) out to save bandwidth.

```text
App Router file-system → URL mapping
app/(marketing)/about/page.js   → /about           (route group invisible in URL)
app/product/[id]/page.js        → /product/123     (dynamic segment)
app/docs/[...slug]/page.js      → /docs/a/b/c       (catch-all, not /docs alone)
app/@analytics + app/@team      → parallel slots passed as props to layout.js
```

**Senior Perspective:**
- Parallel + Intercepting Routes together are the mechanism that makes "app-like modal UX with a real shareable URL" possible without hand-rolled client-side routing hacks — a common frontend-system-design interview probe.
- Choosing App Router over Pages Router for a new project in 2026 isn't a style preference, it's an RSC-by-default architecture decision — a candidate should be able to articulate the bundle-size and SEO implications, not just "it's newer."

### Rendering Strategies: Static, Dynamic, ISR & Partial Prerendering
- The App Router collapses the old SSG/SSR terminology into Static vs. Dynamic rendering, decided automatically by your data-fetching code: cached fetches → rendered once at build time (Static); dynamic functions (reading cookies/headers) or explicitly uncached fetches → rendered per-request (Dynamic).
- ⚖️ Static vs. Dynamic vs. ISR trade-off: Static is fastest/cheapest but can go stale until redeploy; Dynamic (`force-dynamic`) is always fresh but costs a server round-trip per request; Incremental Static Regeneration (`revalidate: N`) is the middle ground — serve stale instantly while regenerating in the background, giving most of Static's speed with bounded staleness.
- Partial Prerendering (PPR) lets a single route mix both: everything outside a `<Suspense>` boundary is prerendered into a static shell served instantly from a CDN, while the dynamic "holes" (personalized cart, recommendations) stream in as they resolve — positioned as the "Holy Grail" because it removes the historical all-static-or-all-dynamic binary choice per route.
- Streaming sends HTML in chunks as each piece becomes ready rather than waiting for the slowest data dependency, directly improving Time to First Byte — the browser renders fast parts (header) immediately while slow parts (a data table) are still being computed server-side.
- 📉 A data-fetching "Waterfall" (sequential awaits blocking each other) is the classic Next.js performance bug; the fix is parallel fetching (`Promise.all` or un-awaited fetch calls resolved later) or, preferably, wrapping each independent data-dependent component in its own `<Suspense>` boundary so Next.js can kick off all fetches simultaneously and stream results independently.
- `searchParams` normally force a whole page dynamic (the server can't know what the user will type) — wrapping the search-dependent component alone in `<Suspense>` keeps the rest of the page static while only that slice becomes dynamic.
- Next.js 15's default caching flip — from "cache everything unless told not to" (`force-cache`) to "fetch fresh every time unless told to cache" (`no-store`, "Dynamic IO") — was a deliberate breaking change to eliminate the extremely common stale-data-in-production bug caused by implicit caching.

```text
Partial Prerendering (PPR):
┌── Static shell (prerendered at build, served instantly from CDN) ──┐
│  Header, nav, product description                                  │
│  <Suspense fallback={<CartSkeleton/>}>                              │
│    <PersonalizedCart/>  ← streamed in dynamically, per-request      │
│  </Suspense>                                                        │
└──────────────────────────────────────────────────────────────────┘
```

**Senior Perspective:**
- The rendering-strategy decision (Static/Dynamic/ISR/PPR) should be made per-route, not per-app — defaulting an entire application to SSR "to be safe" is a common mid-level mistake that throws away Next.js's biggest performance lever.
- Next.js 15's "Dynamic by Default" caching flip is worth knowing precisely because it's a breaking change that bit real production teams — being able to explain *why* the framework made that trade (predictability over implicit performance) demonstrates you track framework evolution, not just API syntax.

### Server Components & the Client Boundary
- Server Components execute only on the server, can `await` a database directly with zero API layer, and contribute zero bytes to the client JS bundle — three things they structurally cannot do: use hooks (`useState`/`useEffect` — no persistent "instance" to hold state), touch browser APIs (`window`/`document`/`localStorage` don't exist server-side), or attach event listeners (`onClick` has nothing to listen on server-side).
- `"use client"` is an opt-in, not a default — the 2026 best practice is "move Client Components to the leaves," keeping the bulk of the tree server-rendered and only marking the small interactive islands (a button, a form, a carousel) as client.
- ⚖️ The "Client Component Tree" rule: once you cross into a Client Component, everything it imports and renders becomes part of the client bundle too — the one escape hatch is passing a Server Component in via the `children` prop, letting a Client Component "wrapper" (a draggable sidebar, a theme provider) host server-rendered content without forcing it into the client bundle.
- Sharing data Server→Client happens via props, which Next.js serializes to JSON under the hood — functions, class instances, and other non-serializable values *cannot* cross that boundary because there's no way to reconstruct live behavior (closures, memory references) from a JSON string on the other side of a server/browser divide.
- The `taint` API (`experimental_taintObjectReference`/`taintUniqueValue`) lets you mark a server-side object (a full User record with a password hash) as forbidden to pass to the client — React throws a hard error at dev time if you accidentally do, closing a real-world data-leak class of bug.

```text
Server/Client boundary with children escape hatch:
<ThemeProvider>          ← "use client" wrapper (needs Context, interactivity)
  <ProductList/>          ← Server Component, passed as children — stays server-rendered,
</ThemeProvider>            zero JS added despite being "inside" a Client Component
```

**Senior Perspective:**
- "Move Client Components to the leaves" is the single most repeated Next.js architecture heuristic for a reason — it's the practical technique that actually delivers RSC's bundle-size promise instead of accidentally clientizing the whole tree via one careless top-level `"use client"`.
- The taint API is a good example of framework-level guardrails against a mistake that used to require code-review vigilance alone — knowing it exists (and why RSC makes this risk newly acute) is a security-mindedness signal.

### Data Fetching, Caching & Server Actions
- Next.js extends the native `fetch` API with two server-side superpowers: automatic caching (so a page refresh doesn't always hit your database) and Request Memoization (if three components on one page call the identical `fetch` URL, only one network request actually fires — the result is broadcast to all three).
- ⚖️ `{ cache: 'force-cache' }` (permanent — fetched once at build, never again until redeploy; for genuinely static data) vs. `{ next: { revalidate: 60 } }` (ISR/stale-while-revalidate — serve cached for 60s, then serve stale-but-trigger-a-background-refetch) — the choice is a direct trade between raw speed and data freshness bounds.
- Server Actions replace hand-rolled API routes for in-app mutations: an async function marked `"use server"` can be called directly from a form/button like a normal function call, eliminating "API glue code" (URL endpoints, fetch boilerplate, type drift between front/back end) — they also support Progressive Enhancement, submitting via standard HTML behavior even if JS hasn't loaded yet.
- Form validation belongs *inside* the Server Action regardless of client-side validation, because client checks are trivially bypassable — returning a structured error object (picked up by `useActionState`, formerly `useFormState`) is the pattern for field-level error display without hand-managed `useState` per form.
- `useOptimistic` implements optimistic UI (instantly flip a "like" heart to red before the server confirms) with automatic rollback on failure — paired with a Server Action, this is the modern replacement for manually managing pending/success/error state per mutation.
- Revalidation is either broad (`revalidatePath('/blog')` — refreshes everything on that URL) or surgical (`revalidateTag('posts')` — refreshes only fetches tagged 'posts', regardless of which page they live on) — tag-based invalidation is the "Pro" choice for apps where the same data surfaces across many layouts.
- Route Handlers (`route.js`) are the modern API-route equivalent, reserved for external communication (mobile clients, third-party webhooks like Stripe) or non-HTML responses (JSON, images, PDFs) — Server Actions are for in-app mutations, Route Handlers are for everything talking to your app from outside it.
- `unstable_cache` extends fetch-style caching/tagging/revalidation to non-fetch data sources (Prisma/Drizzle database calls) that Next.js can't automatically intercept.
- The Data Cache (server-side, remembers fetch results across sessions) is architecturally distinct from the Full Route Cache (stores the entire rendered HTML/RSC payload so a static route doesn't even re-run component code) — understanding both layers is necessary to reason about why a page is or isn't showing fresh data.

```text
Server Action replacing an API route:
Old: Client → fetch('/api/comment', {method:'POST', body}) → Route Handler → DB
New: Client → <form action={addComment}> → Server Action function ("use server") → DB
     (no URL, no fetch boilerplate, progressively enhances without JS)
```

**Senior Perspective:**
- Server Actions collapsing the API-route ceremony for in-app mutations is a genuine architectural shift — a senior engineer should know when a Route Handler is still the right call (external consumers, non-HTML responses) rather than defaulting everything to Server Actions.
- Tag-based revalidation (`revalidateTag`) vs. path-based (`revalidatePath`) is the kind of caching-granularity decision that separates "it works" from "it scales to a real multi-surface application" — worth walking through explicitly in a system-design answer.

### Middleware, Auth & Security
- Middleware (`middleware.ts`) runs in the lightweight Edge Runtime — geographically close to the user, zero cold start — intercepting a request before it completes, most commonly for auth guarding (check session cookie, redirect unauthenticated users to `/login` before the private page is even built server-side) and A/B testing.
- ⚖️ Edge Runtime limitations are a real trade-off: no Node.js APIs (`fs`, `path`), only standard Web APIs, small code-size limits — heavy database calls or slow external APIs inside Middleware directly slow down *every* request on the site; the professional pattern is "logic-only" Middleware (read cookies/headers, redirect) with actual data fetching deferred to Server Components.
- Restricting Middleware's `matcher` config to only the routes that need it (protected sections, not static assets) is a required performance practice — unrestricted Middleware runs on every single request including images and CSS.
- CSRF protection is built into Server Actions via Origin/Referer header checks, hardened further with `SameSite` cookie settings, re-verifying the session inside the action (never trust client-side auth state alone), and tying forms to `useActionState`.
- `NEXT_PUBLIC_` prefix is the explicit opt-in for exposing an environment variable to the browser bundle — everything else defaults to server-only, a secure-by-default posture.
- NextAuth.js/Auth.js integrates via Route Handlers (`/api/auth/[...nextauth]`), Server Actions (`signIn()`/`signOut()`), and Middleware helpers, and is the de facto standard because it encodes modern security practices (session encryption, provider OAuth flows) without requiring the team to be security experts.
- ⚖️ Server-side session reads (via `auth()` in Server Components, instant, no loading state) vs. client-side session reads (`useSession()` + `<SessionProvider>`, reactive to client-side logout) — server-side should be the primary source, client-side is a reactive backup for interactive components only.
- Rate limiting (via Upstash/Vercel KV checked in Middleware at the Edge) protects the origin server/database from brute-force or bot traffic by returning `429 Too Many Requests` before the request reaches expensive backend logic.

```text
Auth-guarded request flow:
Request /admin → Edge Middleware checks session cookie
   valid    → request proceeds to Server Component (renders private data)
   invalid  → redirect to /login BEFORE any private data is ever fetched/sent
```

**Senior Perspective:**
- Keeping Middleware "logic-only" and pushing real data work into Server Components is the correct default — the Edge Runtime's restrictions aren't arbitrary, they're the cost of near-zero cold start, and violating that boundary silently slows down every request on the site.
- Server-Action CSRF protection being "on by default" (Origin/Referer checks) doesn't remove the need for defense in depth — re-verifying auth state server-side inside every mutation, not just trusting a client-passed flag, is the senior-level instinct interviewers probe for.

### Performance Optimization & Build Tooling
- The `<Image/>` component automates what a raw `<img>` leaves manual: device-appropriate sizing, modern-format conversion (WebP/AVIF), default lazy-loading, and required width/height that reserves layout space to prevent Cumulative Layout Shift; `priority` opts the above-the-fold hero image out of lazy-loading and preloads it, directly improving Largest Contentful Paint (a Google ranking factor).
- `<Script/>` strategies schedule third-party JS deliberately: `beforeInteractive` (critical, blocking — bot detectors/polyfills only), `afterInteractive` (default — analytics/tag managers), `lazyOnload` (fully idle — chat widgets) — this prevents third-party scripts from silently degrading your own app's interactivity metrics.
- `next/font` self-hosts and optimizes fonts at build time, producing "zero-runtime CSS" (no client-side JS needed to determine font metrics) and using automatic size-adjustment so a fallback font occupies identical space to the custom font, eliminating font-swap layout shift entirely.
- The Metadata API (static `metadata` object, or `generateMetadata()` for per-page dynamic titles/descriptions fetched from a database) is the framework-native replacement for manually managing `<head>` tags, with `sitemap.js`/`robots.js` keeping SEO files in sync with live data instead of hand-maintained static files.
- ⚖️ Turbopack (Rust-based, Next.js's Webpack successor) claims up to 700x faster local dev rebuilds via an incremental engine that only recalculates the specific changed code — the trade-off consideration for a senior engineer is ecosystem/plugin maturity vs. Webpack's, not raw speed alone.
- The Bundle Analyzer visualizes exactly which dependencies bloat the production bundle (a "treemap"), the practical tool for hunting oversized libraries before they become a Core Web Vitals problem; Barrel Files (`index.js` re-exporting an entire folder) can force build tools to process every file in a folder even when only one export is used — a known large-project pitfall to watch for in code review.

**Senior Perspective:**
- Image-priority discipline (`<Image priority/>` on the LCP element, explicit dimensions everywhere) is one of the highest-leverage, lowest-effort Core Web Vitals wins available — a senior engineer treats it as a default, not an afterthought optimization pass.
- Knowing *why* Turbopack is fast (incremental, per-file recalculation vs. Webpack's broader re-processing) rather than just "it's faster" is the difference between reciting a marketing claim and understanding the architecture.

### Deployment, Edge & Migration
- ⚖️ Serverless Functions (full Node.js, heavy tasks, but cold starts and single-region) vs. Edge Functions (lightweight, zero cold start, run physically close to the user, but restricted runtime — no heavy Node.js libraries) — the trade-off is raw capability vs. latency/global distribution, and the right choice depends on whether the task is "quick and latency-sensitive" (redirects, A/B tests, auth checks) or "heavy and capability-dependent" (PDF generation, complex DB math).
- Open Next is an adapter that makes a Next.js build portable to any cloud (AWS, Cloudflare, Azure) instead of features like ISR/Middleware/Image Optimization being implicitly Vercel-infrastructure-dependent — the enterprise motivation is avoiding vendor lock-in while keeping the App Router's full feature set.
- `output: 'export'` produces a pure static-file build deployable to any static host (S3, GitHub Pages) at the cost of losing every feature requiring a live server: Server Actions, dynamic SSR (cookies/headers), Middleware, and the built-in Image Optimization API — appropriate for docs/blogs/marketing sites, not for anything needing real-time server logic.
- 📉 Debugging in production requires visibility tooling by design (you can't attach a breakpoint to a user's browser): error tracking (Sentry/LogRocket) for exact failure state capture, server-side/hosting-provider logs for cache/revalidation visibility (Next.js 15+ has notably improved verbose fetch-cache logging), Core Web Vitals dashboards for real-user metrics your dev laptop won't reproduce, and uploaded source maps so minified production stack traces map back to real code.
- 👥 The senior-level migration playbook for a large Pages Router app: coexist (App Router and Pages Router run in the same project simultaneously — never a big-bang flip), convert static/simple pages first for immediate wins, bridge global state (wrap the App Router root layout in a client-side Provider so old and new pages share the same store), migrate shared components bottom-up ("leaf strategy"), and save complex dashboard/checkout flows for last once the rest is stable — this reduces catastrophic-failure risk while the team keeps shipping features throughout.

```text
Edge vs. Serverless trade-off:
Edge Function:      close to user, ~0ms cold start, restricted runtime  → redirects, auth checks, A/B tests
Serverless Function: regional, cold-start delay, full Node.js runtime   → PDF generation, heavy DB queries
```

**Senior Perspective:**
- Open Next existing at all is a tell about Next.js's own architecture — several headline features are genuinely coupled to Vercel's infrastructure by default, and a staff engineer evaluating Next.js for an enterprise with existing AWS/GCP commitments needs to know that up front, not discover it during deployment.
- The "coexistence, never big-bang" migration strategy is the answer that separates a candidate who's actually run a large legacy migration from one who's only read about App Router in isolation — it's explicitly the same staged-de-risking philosophy that shows up in the Angular Zoneless migration and any serious framework-version-upgrade project.

**Predictive Interview Questions (Next.js):**
1. Walk me through what happens end-to-end when a user visits a Partial-Prerendered route for the first time — what's served from the CDN instantly, what streams in afterward, and what determines the Suspense boundary?
2. Your team has a dashboard page where five different components each independently fetch the "current user" data via `fetch()`. Is this actually a performance problem in the App Router, and how would you verify your answer?
3. Tell me about migrating (or evaluating a migration of) a production app from the Pages Router to the App Router. What went first, what did you deliberately save for last, and what would have gone wrong if you'd tried to convert it all at once?

**Executive Summary Cheat Sheet (Next.js):** Next.js's App Router architecture is built on React Server Components by default, which is the structural reason it ships less client JavaScript than the legacy Pages Router, and its rendering model (Static/Dynamic/ISR/PPR, chosen per-route) replaces the old all-or-nothing SSR-vs-SSG choice with fine-grained control. At senior level, the recurring judgment calls are where to draw the Server/Client Component boundary ("move Client Components to the leaves"), Server Actions vs. Route Handlers based on internal-vs-external callers, and Edge vs. Serverless based on latency-sensitivity vs. runtime capability needs.

## Tailwind CSS

### Utility-First Philosophy & Build Architecture
- 🏗️ Tailwind's core bet is Utility-First: compose UI from small, single-purpose, atomic classes (`flex items-center`) directly in markup instead of authoring semantic class names (`.header-container`) backed by separate CSS — the win is that the "source of truth" for an element's styling is on the element itself, with zero file-switching to understand what it looks like.
- ⚖️ Component-based (semantic classes like `.btn-primary`) vs. utility-based CSS: semantic classes are reusable at the CSS layer but accumulate "override bloat" (`.btn-primary-small`) as variants multiply; utility classes push reuse to the *component* layer (a React `<Button/>`) instead — Tailwind deliberately encourages JS/framework components for reuse rather than CSS components.
- Just-In-Time (JIT) compilation scans your actual source files (via the `content` array in config) and generates CSS only for classes you literally use — this is *why* a Tailwind production bundle is typically under 10KB gzipped even on massive projects, versus generating every possible class combination upfront.
- ⚖️ Tailwind vs. pure inline styles: both look similarly "inline" in markup, but Tailwind produces a cacheable static CSS file (downloaded once, reused across page loads) and supports media queries, hover/focus/active pseudo-states, and pseudo-elements — none of which raw inline styles can express at all.
- Preflight is a global reset (built on modern-normalize) that strips browser default styling and makes elements "unstyled by default" (an `<h1>` has no inherent size/weight until you add `text-3xl font-bold`) — this eliminates the constant "fighting browser defaults" tax of traditional CSS.
- Tailwind is technically a PostCSS plugin, not a standalone preprocessor — it reads your config and source files and injects generated utility classes into the CSS pipeline, which is why it composes cleanly alongside tools like Autoprefixer rather than needing to reimplement CSS parsing itself.
- The three-layer cascade (`base` → `components` → `utilities`) is ordered deliberately so utility classes (highest layer) always win over component classes — without that ordering, a utility override like `hidden` could silently fail to beat a `.modal` component class.
- ⚖️ `@apply` (baking utilities into a custom CSS class) is officially discouraged for routine use — it reintroduces CSS bloat, brings back "naming fatigue," and loses the whole point of utility-first (seeing exactly what an element looks like by reading its HTML); the Tailwind team's recommended reuse mechanism is JavaScript/framework components, not `@apply`.

```text
JIT pipeline:
Source files (content array) → scan for full class-name strings → generate only matched CSS
   → PostCSS pipeline (Autoprefixer, cssnano minify) → final CSS (often <10KB gzipped)
```

**Senior Perspective:**
- The utility-vs-semantic-CSS debate is really a "where does reuse live" architecture question — Tailwind's answer (push reuse to the component layer, not the CSS layer) only works if your team is already component-disciplined, which is why it pairs so naturally with React/Vue/Angular but less naturally with a legacy jQuery-style codebase.
- `@apply` overuse is a code-review smell worth calling out explicitly — teams that reach for it reflexively are usually trying to force Tailwind back into a component-based CSS mental model instead of embracing the framework-component reuse pattern it was actually designed around.

### Configuration & Design System Scaling
- ⚖️ `theme: {...}` (full override — replaces Tailwind's entire default scale, e.g. all default colors stop working) vs. `theme: { extend: {...} }` (additive — keeps every default while layering custom values on top) — `extend` is correct ~95% of the time; a bare `theme` override is a rare, deliberate "start from scratch" decision.
- Arbitrary values (`top-[117px]`, `bg-[#bada55]`) let JIT generate one-off classes outside the design scale on demand — legitimate for genuinely unique cases (a precise icon position, a brand-specific hex) but bad practice for routine spacing/color, where it silently breaks the consistency a design system exists to enforce.
- Custom plugins (via `plugin()` + `addUtilities`) extend Tailwind with CSS properties it doesn't ship out of the box (e.g., `text-shadow-md`) while keeping them integrated into the same utility-class system rather than floating in a separate global stylesheet.
- 📉 Design token pipelines (Figma Variables → JSON → Style Dictionary or a Figma plugin → `tailwind.config.js`) establish a single source of truth between design and code — when a designer updates the brand primary color in Figma, the config updates on the next build, eliminating the classic "the hex code in code doesn't match Figma anymore" drift.
- Tailwind Presets (`presets: [require('@company/tailwind-preset')]`) let a monorepo share one base configuration (brand colors, fonts, spacing) across multiple apps (marketing site, dashboard, mobile) — a rebrand becomes a single preset-file change instead of N config files to keep in sync.
- The `theme()` and `screen()` CSS functions pull config values (colors, spacing, breakpoints) into hand-written custom CSS, keeping "escape hatch" CSS connected to the same design tokens instead of hard-coding magic numbers that drift from the config over time.

```text
Design token flow:
Figma Variables → export JSON → Style Dictionary transform → tailwind.config.js
   → single source of truth: designer changes primary color → next build updates every consuming app
```

**Senior Perspective:**
- Presets in a monorepo are the direct Tailwind answer to "how do we keep five product surfaces visually consistent without five copy-pasted configs" — a standard staff-level frontend-platform interview scenario.
- Treating `tailwind.config.js` as the codified design system (not just a styling config) is the mental shift that makes design-token pipelines make sense — a senior engineer frames config changes as design-system governance, not CSS tweaks.

### Responsive Design, State Variants & Dark Mode
- Tailwind is mobile-first by default: an unprefixed class applies at all sizes, and a breakpoint prefix (`md:`) generates a `min-width` media query — meaning `md:text-left` applies at 768px *and up*, encouraging "design small, layer complexity in" rather than the max-width, desktop-first alternative.
- Modifiers stack freely (`hover:active:bg-blue-700`, `sm:hover:active:disabled:opacity-50`) — JIT's unlimited-variant generation is what makes arbitrarily deep interaction-state targeting possible without CSS file-size blowing up.
- The `group`/`group-hover:` pattern styles a child based on a parent's state (a card's text color changing when the whole card is hovered); the `peer`/`peer-checked:` pattern styles a *sibling* based on an input's state (a label styled based on a checkbox) via the CSS subsequent-sibling combinator — both are pure-CSS interactivity with zero JavaScript.
- ⚖️ Dark mode strategies: `media` (default — follows the OS `prefers-color-scheme` setting automatically, zero app logic) vs. `class` (looks for a `.dark` class on a parent element — required if you want to offer the user a manual theme toggle) — `class` is the professional choice whenever the product needs a user-facing theme switch rather than pure OS-following.
- Container Queries (`@container` on a parent, `@md:flex-row` on a child) ask "how wide is my *parent*," not "how wide is the *browser*" — this is what makes a genuinely reusable Card component look right whether it's dropped into a narrow sidebar or a wide hero section, something media queries alone can't express per-component.

```text
Mobile-first breakpoint cascade:
<div class="flex-col md:flex-row lg:gap-8">
  base (no prefix): flex-col applies to ALL sizes
  md: (≥768px):     flex-row overrides, stays active through lg/xl/2xl
  lg: (≥1024px):    gap-8 layers on top
```

**Senior Perspective:**
- `class`-strategy dark mode is the correct default for any product offering a user-facing theme toggle — reaching for `media` in that scenario is a common implementation mistake that quietly breaks the UX the product actually asked for.
- Container Queries are the answer to "why does my reusable Card component look wrong depending on where I drop it" — recognizing this as a *component-scoped responsiveness* problem, distinct from page-level media queries, is a genuine CSS-architecture maturity signal.

### Component Reuse & Framework Integration
- ⚖️ Tailwind cannot resolve dynamically-constructed class strings (`"bg-" + color + "-500"`) because its JIT scanner looks for complete, static strings at build time — the fix is a mapping object (`{ red: 'bg-red-500', blue: 'bg-blue-500' }`) so the full class strings exist literally in source and are scannable, or a config `safelist` (regex-based) for cases a mapping object can't cover.
- `tailwind-merge` intelligently resolves class conflicts when a reusable component accepts a `className` prop from its consumer (e.g., internal `mt-4` + consumer-passed `mt-10` — plain string concatenation leaves both in the DOM with undefined cascade-order behavior; `tailwind-merge` understands Tailwind's semantics and correctly replaces `mt-4` with `mt-10`) — essential for any component library built on Tailwind.
- Headless UI (built by Tailwind Labs) ships fully-functional, zero-CSS components (Modal, Dropdown, Toggle) with complex behavior (keyboard navigation, screen-reader support) pre-solved — you supply 100% of the visual design via Tailwind classes, avoiding both "build accessible JS logic from scratch" and "fight pre-styled opinions that don't match your brand."
- The `prose` class (Tailwind Typography plugin) retroactively styles unclassed, CMS/Markdown-generated HTML (blog posts, docs, legal pages) with proper font sizing/line-height/spacing — solving the specific problem that raw database-sourced HTML has no Tailwind classes on its tags at all.
- `@tailwindcss/forms` resets browser-default form styling (which is otherwise nearly unstylable for checkboxes/radios) into a neutral base that's trivially customizable with standard utility classes (`text-blue-500` for fill, `rounded` for corners).
- Tailwind pairs naturally with component-based frameworks (React/Vue/Angular) because both already divide UI into isolated pieces — utility classes are inherently scoped to the element they're on, so there's no class-name-collision risk (`.title` in one component clobbering `.title` in another) the way global semantic CSS has.

```text
tailwind-merge conflict resolution:
Internal:  <Button className="mt-4 px-2">        (component default)
Consumer:  <Button className="mt-10">             (override intent)
Without merge: class="mt-4 px-2 mt-10"  → undefined which margin wins
With merge:    class="px-2 mt-10"       → mt-4 correctly replaced
```

**Senior Perspective:**
- `tailwind-merge` is not optional plumbing for a serious component library — without it, every consumer-supplied `className` override is a coin-flip CSS bug waiting to happen, exactly the kind of "looks fine until it doesn't" defect that erodes trust in a shared component system.
- Headless UI + Tailwind is the pragmatic middle ground between "build every accessible interactive component from scratch" and "adopt a fully-styled component library and fight its opinions" — recommending this combination shows awareness of the accessibility cost most teams underestimate.

### Layout, Performance & Accessibility
- ⚖️ Grid vs. Flexbox in Tailwind: `grid-cols-12` suits strict, cross-row-aligned layouts (dashboards, forms, magazine-style pages); `flex` suits dynamic, content-driven layouts (nav links, tag rows) that need to wrap/grow based on content — the rule of thumb is Grid for the page's overall skeleton, Flex for the muscles/joints inside components.
- `aspect-video`/`aspect-square` (or an arbitrary `aspect-[4/3]`) reserve a shape before content loads, replacing the old padding-bottom-percentage hack — this, plus explicit `w-`/`h-` sizing and `min-h-[]` for dynamic sections, is Tailwind's direct toolkit for reducing Cumulative Layout Shift.
- The Z-index scale (`z-10` through `z-50`, only effective on positioned elements) can be extended with named tokens (`zIndex: { modal: '100', dropdown: '50' }`) to prevent the "Z-index war" anti-pattern where teams escalate to `z-[9999]` reflexively instead of maintaining an intentional layering system.
- The recommended production pipeline is Integrated JIT via a framework's built-in PostCSS plugin (Next.js/Vite/Nuxt): scan source → generate minified CSS containing only used classes → post-process with Autoprefixer + cssnano — the resulting file is typically under 10KB and requires no separate build step to maintain.
- For animation, the professional split is Tailwind for the *initial/final state* (`opacity-0 scale-95` → `opacity-100 scale-100`, or simple `transition-all duration-300`) with a dedicated animation library (Framer Motion, GSAP) handling complex layout/transform tweening — Tailwind classes should stay static during a complex animation rather than being toggled rapidly.

```text
Layout tool selection:
Page skeleton (header/sidebar/footer, cross-aligned rows/columns)  → Grid (grid-cols-12)
Component internals (nav links, tag chips, button groups)          → Flex (flex flex-wrap gap-2)
```

**Senior Perspective:**
- CLS reduction via `aspect-*` + explicit dimensions is a near-zero-cost, high-leverage Core Web Vitals fix that should be a default habit, not a remediation task discovered during a Lighthouse audit.
- The Grid-for-skeleton, Flex-for-components heuristic is a fast, teachable rule that resolves most "should I use grid or flex here" debates in code review without a lengthy discussion each time.

**Predictive Interview Questions (Tailwind):**
1. Explain exactly why `<div className={"bg-" + color + "-500"}>` fails to generate the expected styles in production, and walk through two different ways to fix it.
2. You're building a component library shared across five product teams. What role does `tailwind-merge` play, and what breaks in consumer code if you skip it?
3. Tell me about a time you had to scale a design system (Tailwind or otherwise) across multiple teams or products. How did you keep visual consistency without slowing every team down with a shared config bottleneck?

**Executive Summary Cheat Sheet (Tailwind CSS):** Tailwind's utility-first philosophy pushes styling reuse to the component layer (via React/Vue/Angular components) rather than the CSS layer (via semantic classes), which is why it pairs naturally with modern component frameworks and stays fast via JIT compilation that generates only the CSS you actually use. At senior level, the recurring judgment calls are `extend`-vs-override in config, Grid-vs-Flex for skeleton-vs-component layout, and knowing when `@apply`/arbitrary values are a legitimate escape hatch versus a sign the design system discipline is breaking down.

## JavaScript Essentials for React

Modern React leans heavily on core JavaScript (ES6+) fluency — closures, destructuring, async control flow, and functional idioms show up in nearly every hook and component. This section is a quick-fire reference for the JS fundamentals interviewers expect a React candidate to have cold.

### Variables, Functions & Control Flow

**Q: `var` vs. `let` vs. `const`?**
`var` is function-scoped; `let` is block-scoped; `const` can only be assigned once — its binding can't be reassigned afterward (note: for objects/arrays, the *contents* can still be mutated, only the reference is locked).

**Q: What are the types of conditional statements in JS?**
`if`/`else` statements, the ternary operator, and `switch` statements.

**Q: What is error handling in JS?**
The process of anticipating and managing runtime errors gracefully — most commonly via `try`/`catch`/`finally` blocks, so a failure doesn't crash the whole program.

**Q: Spread vs. Rest operator — what's the difference?**
Both use `...`, but in opposite directions: the *spread* operator expands an iterable (array, string, object) into individual elements (copying an array, merging arrays, passing multiple arguments to a function). The *rest* operator does the reverse — it collects remaining function arguments into a single array.

**Q: What are arrays, and how do you get/add/remove elements?**
An array stores multiple values in a single variable. Common methods: get (`indexOf`, `find`, `filter`, `slice`), add (`push`, `concat`), remove (`pop`, `shift`, `splice`), modify/iterate (`map`, `forEach`), and others (`join`, `length`, `sort`, `reverse`, `reduce`, `some`, `every`).

**Q: What is array destructuring?**
An ES6 feature that extracts elements from an array into individual named variables in a single statement, e.g. `const [first, second] = myArray`.

**Q: What are functions, and what types exist in JS?**
A function is a reusable block of code that performs a specific task. Types: named functions, anonymous functions, function expressions, arrow functions, IIFEs, callback functions, and higher-order functions.

**Q: Named vs. anonymous functions — when do you use each?**
Named functions have an identifier and are best for larger, reused logic. Anonymous functions have no name and suit small, one-off logic used in a single place.

**Q: What is a function expression?**
Defining a function by assigning it to a variable, e.g. `const add = function(a, b) { return a + b; }`.

**Q: What are arrow functions, and what are they used for?**
A more compact syntax for defining functions using `=>` — widely used for callbacks and short function bodies.

**Q: What are callback functions?**
Functions passed as an argument to another function, to be invoked by that function.

**Q: What is a higher-order function?**
A function that either takes one or more functions as arguments (e.g. a callback), or returns a function as its result (or both).

**Q: Pure vs. impure functions?**
A pure function always returns the same output for the same input, and causes no side effects or state mutation. An impure function can return different outputs for the same input and may mutate state or produce side effects.

### Objects, Strings & Async

**Q: What are template literals?**
An ES6 (backtick `` ` ``) string syntax supporting embedded expression interpolation (`` `Hello ${name}` ``) and multi-line strings without manual concatenation.

**Q: What are objects in JS?**
A data type that stores key-value pairs; values can be strings, numbers, booleans, `null`/`undefined`, arrays, functions, or other objects.

**Q: Array vs. object — what's the difference?**
An array is an ordered, index-based collection, best for lists. An object is an unordered collection of named (keyed) properties, best for labeled/structured data. *(The source book's slide for this question didn't retain readable text in extraction — this answer reflects standard JS semantics rather than book-specific wording.)*

**Q: How do you add, modify, or delete a property on an object?**
Add or modify with `obj.key = value` (or `obj['key'] = value`); delete with `delete obj.key`. *(Same extraction caveat as above.)*

**Q: What is asynchronous programming, and what is it used for?**
A style where multiple operations can be started and run without blocking the rest of the code from executing while they complete. Typical uses: fetching data from an API, uploading/downloading files, animations/transitions, and other time-consuming operations.

**Q: Synchronous vs. asynchronous programming?**
Synchronous code runs top-to-bottom, each statement blocking the next until it finishes. Asynchronous code can kick off an operation and let other code keep running while that operation completes in the background. *(Extraction caveat as above.)*

**Q: What are Promises in JavaScript?**
An object representing a value that isn't available yet but will be at some point. A Promise is always in one of three states: pending, resolved (fulfilled), or rejected.

**Q: How do you implement a Promise?**
Construct one with `new Promise((resolve, reject) => { ... })`, and consume it with `.then()`/`.catch()` chaining or with `async`/`await`. *(Extraction caveat as above.)*

```js
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
```

**Q: What is the purpose of `async`/`await`, compared to Promises?**
`async` marks a function as asynchronous, so its internal code doesn't block other code from running. `await` (used only inside an `async` function) pauses that function's execution until the awaited Promise resolves or rejects. It's syntactic sugar over `.then()` chains that lets asynchronous code read like ordinary synchronous code.

### Classes & `this`

**Q: What are classes in JS?**
Blueprints for creating objects that define their structure and behavior. Benefits: object creation, encapsulation, inheritance, code reusability, polymorphism, and abstraction.

**Q: What is a constructor?**
A special method inside a class that's automatically invoked when a new instance is created with `new`.

**Q: What is the `this` keyword used for?**
It provides a way to access the current object or class instance from within a method.

## TypeScript

TypeScript questions round out the "Bonus" chapters of the source material — foundational typing, OOP concepts, and how they map onto (and beyond) plain JavaScript.

### Types & the Compiler

**Q: What is TypeScript, and what are its advantages over JavaScript?**
TypeScript is an open-source, strongly-typed superset of JavaScript with object-oriented features that catches type errors at compile time. Browsers can't execute TypeScript directly — the TypeScript compiler (`tsc`) transpiles it down to plain JavaScript first.

**Q: How do you install TypeScript and check its version?**
```bash
npm install -g typescript
tsc --version
```

**Q: `let` vs. `var` in TypeScript?**
Same as in JavaScript: `var` is function/globally scoped, `let` is block-scoped — a `let` loop variable declared inside a `for` loop isn't accessible outside it, while a `var` one is (and reusing it outside the loop is legal, if usually a bug smell).

**Q: What is type annotation?**
An explicit type declaration on a variable (e.g. `let i: number`) that lets the compiler check assignments against that type and flag mismatches at compile time rather than at runtime.

**Q: What are built-in/primitive vs. user-defined/non-primitive types?**
Built-in/primitive types store simple values: `string`, `number`, `boolean`. User-defined/non-primitive types store more complex data: arrays, enums, classes, interfaces.

**Q: What is the `any` type?**
A type that opts a variable out of type-checking entirely — the compiler allows assigning any kind of value to it with no compile-time error, at the cost of losing type safety for that variable.

**Q: What is an enum?**
A way to define a set of named constants. Useful for a fixed family of related values (e.g. compass directions) — using named members instead of raw numbers means inserting a new member later doesn't force you to renumber everything by hand.

**Q: `void` vs. `never` — what's the difference?**
`void` means "no return value" — used for functions that don't return anything meaningful. `never` means the function never successfully returns at all — used for functions that always throw or otherwise never complete normally.

**Q: What is type assertion?**
A way to tell the compiler to treat a value as a specific type (e.g. `<string>someValue` or `someValue as string`), overriding TypeScript's own inferred type and skipping its automatic type-checking for that value.

**Q: What are arrow functions in TypeScript?**
The same `=>` syntax as JavaScript — a more compact alternative to a traditional function expression, fully typed like any other TS function.

### Object-Oriented TypeScript

**Q: What is Object-Oriented Programming in TypeScript?**
A design approach for building structured, maintainable applications around four pillars: encapsulation, inheritance, polymorphism, and abstraction.

**Q: What are classes and objects?**
A class is the blueprint defining properties and methods; an object is an *instance* of that class, created from it, used to set its properties and call its methods.

**Q: What is a constructor (in a TS class)?**
A method automatically invoked when a class is instantiated. It always runs before any other class logic (and, in Angular specifically, before any lifecycle hook) — commonly used to inject dependencies or initialize properties.

**Q: What are the access modifiers in TypeScript?**

| Modifier | Accessible from |
|---|---|
| `public` | Anywhere (the default) |
| `private` | Only within the same class |
| `protected` | The class itself and its subclasses |

**Q: What is encapsulation?**
Bundling data together with the functions that operate on it — typically by making a field `private` and exposing controlled access through public methods (e.g. a `getEmpId()` getter). This protects against direct, unchecked access to internal data.

**Q: What is inheritance?**
A derived/child class automatically acquires the properties and methods of its base/parent class without rewriting them — e.g. `Dog` and `Cat` classes extending an `Animal` base class automatically get its `eat()`/`sleep()` methods. This is the mechanism behind code reuse across related classes.

**Q: What is polymorphism?**
The ability for a method with the same name to behave differently depending on which class's instance it's called on — e.g. a subclass overriding a base class's `getName()` with its own implementation, so the same call produces different results for different objects.

**Q: What is an interface, and why use one?**
A contract that declares method/property signatures without implementing them. Classes that implement an interface must each supply their own implementation — this keeps a family of related classes (e.g. `PermanentEmployee`, `ContractEmployee`) consistent, makes unit testing easier, and is TypeScript's route to achieving multiple inheritance.

**Q: `extends` vs. `implements`?**
`extends` is used for inheriting from a base *class*. `implements` is used for fulfilling an *interface's* contract.

**Q: Is multiple inheritance possible in TypeScript?**
Not via classes directly (a class cannot `extend` more than one class) — but it's achievable by having a class `implements` multiple interfaces.
