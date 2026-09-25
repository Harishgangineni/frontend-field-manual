# Pillar: Algorithms & Problem Solving

DSA still matters at senior level for a frontend role, but the bar moves from "can you produce a working solution" to "how do you reason about it out loud and connect it to production reality." Nobody is grading whether you memorized the three-reversal trick for array rotation — they're grading whether you can name the pattern in five seconds, articulate the time/space trade-off against the naive approach, and translate it into something that matters in a browser: a virtualized list, a debounced search box, a trie-backed autocomplete, a diffing algorithm. The senior signal is pattern recognition plus communication plus systems-thinking about where these primitives actually live in a frontend codebase — not raw LeetCode throughput.

## Complexity Analysis & Trade-offs

- 📉 Big-O is a proxy for real bottlenecks: an O(N²) nested loop over a 50-element array is invisible in a profiler, but the same shape over a 50,000-row data grid or a keystroke-driven autocomplete list is the actual jank a user reports. Reasoning about complexity out loud is really reasoning about *when this stops being fine*.
- 🏗️ Hash tables achieve average O(1) lookup by combining an array with a hash function that maps a key to a direct memory index — the array gives O(1) access by address, the hash function computes that address without scanning. Collisions (two keys landing on the same index) are the failure mode, typically resolved with separate chaining (an array/list per bucket); building one from scratch (as in a `HashMap` class with a `hash()` function summing char codes mod bucket size) is the fastest way to prove you understand *why* `Map`/`Object` lookups are fast rather than just using them.
- ⚖️ Time vs. space is the recurring trade-off across this whole pillar: Kadane's algorithm and Boyer-Moore voting hit O(1) space by tracking only a running value instead of memoizing every subproblem; memoized recursion (Fibonacci, DP tabulation) spends O(N) space to avoid O(2^N) recomputation. Neither is "correct" in isolation — you're trading memory you have plenty of for CPU time users can feel, or vice versa on a memory-constrained device.
- ⚖️ Readability vs. micro-optimization: index-mapping tricks (e.g., negating array values in-place to detect duplicates in O(1) space, or the three-step reversal for array rotation) shave allocations but make code harder to review and more bug-prone under maintenance. In an interview, name the O(1)-space trick to show you know it exists, then say out loud whether you'd actually ship it over the simpler O(N)-space version in a codebase other engineers will touch.
- 📉 Sort stability is a correctness property, not a performance one, but it's exactly the kind of subtle bug that ships silently: JavaScript's `Array.prototype.sort()` is spec-guaranteed stable, meaning elements with equal sort keys keep their original relative order. This matters the moment you sort by multiple criteria in sequence (e.g., a table already sorted by date, then re-sorted by department) — an unstable sort would scramble the secondary ordering and nobody would notice until a user complains their data looks "randomly shuffled."

**Senior Perspective:**
- Lead with the pattern name ("this is sliding window," "this is Union-Find") before writing code — it signals recognition, not trial-and-error.
- Always state the trade-off you're accepting, not just the complexity you achieved — "O(1) space but the array is now unreadable garbage" is a stronger answer than silently writing the optimized version.
- Tie complexity claims to a concrete scale number when possible ("fine up to a few hundred rows, falls over past low thousands without virtualization") — this is what separates senior framing from reciting Big-O notation.

## Arrays, Strings, Hashing & Two-Pointer / Sliding-Window Patterns

```text
Two Pointers:  Input ➔ left=0, right=len-1 ➔ Compare/Combine ➔ Shrink from one side ➔ Result
Sliding Window: Input ➔ expand right, track window state ➔ window invalid? shrink left ➔ record best ➔ Result
```

- 🏗️ Two-pointer is the default for "sorted or symmetric input, find a pair/triplet/region": palindrome check, Two Sum (hash-based, O(N)) vs. Three Sum (sort + two-pointer, O(N²) but O(1) extra space beyond output), merging two sorted arrays, container-with-most-water, trapping rain water, and moving/deduping elements in-place (move zeros, remove duplicates from sorted array, next permutation's swap-and-reverse tail). The unifying idea: sorted or bounded input lets you eliminate half the search space per comparison instead of re-scanning.
- 🏗️ Sliding window covers two variants — fixed-size (max sum of a size-k subarray: maintain a running sum, add the new right element, subtract the element leaving on the left) and variable-size (longest substring without repeating characters, longest substring after at most k character replacements, minimum-length subarray meeting a sum target, all anagram start-indices of a pattern in a string). The variable window expands right until a Set/frequency-map invariant breaks, then contracts left until it's valid again — never re-scanning from the start.
- ⚖️ Kadane's algorithm (max subarray / max product subarray) trades a full O(N²) brute-force scan of every subarray for O(N) by asking one local question at each index: "extend the running subarray, or start fresh here?" Max *product* subarray complicates this because a negative number can flip a historically-bad product into the new best — you must track both a running max and a running min, swapping them when the current number is negative.
- ⚖️ Prefix-sum + hash map (subarray sum equals K) trades a nested-loop O(N²) sum check for O(N) by storing cumulative sums seen so far and asking "does `currentSum - k` already exist?" — this is the same "complement lookup" idea as Two Sum, generalized from pairs to subarray ranges. Product-of-array-except-self applies the same prefix/suffix trick to avoid division entirely: one left-to-right pass builds prefix products, one right-to-left pass multiplies in suffix products.
- 👥 Hashing/frequency patterns are the bread-and-butter of "explain your reasoning while coding" rounds because they're conceptually simple but reveal whether you reach for the right tool: anagram/first-non-repeating-character checks (frequency counters), group anagrams (sorted-string or char-count as a hash key), majority element (Boyer-Moore voting — O(1) space candidate/counter instead of a frequency map), longest consecutive sequence (a Set for O(1) membership checks, only starting a scan from numbers with no left-neighbor to guarantee O(N) total), first missing positive (index-mapping the array onto itself since answers are bounded by array length), top-K-frequent (bucket sort by frequency to beat O(N log N) sorting), and isomorphic strings / word pattern (bidirectional maps to guarantee a strict one-to-one relationship, not just one-directional).
- 🏗️ Reimplementing `Array.prototype.map/filter/reduce` from scratch is a recurring "prove you understand the abstraction" ask — it forces you to handle the callback signature `(element, index, array)`, sparse-array holes (`i in this`), and `reduce`'s messy initial-value/empty-array edge cases. This is the same muscle used when reviewing or building custom hooks and utility libraries: you should be able to explain *why* these methods exist as immutable, non-mutating operations before reaching for them blindly.
- ⚖️ In-place string/number formatting problems (string compression, spiral matrix traversal, Pascal's triangle, zigzag string conversion, reverse-integer/atoi with 32-bit overflow handling, Roman numeral conversion, integer division without the `/` operator via bitwise doubling, `pow(x, n)` via binary exponentiation) all trade a small amount of code complexity for either O(1) extra space or O(log N) time instead of O(N) — the common thread is simulating a mathematical process (digit extraction, boundary tracking, repeated squaring) instead of leaning on built-ins that don't exist in the constrained version of the problem.

**Senior Perspective:**
- Two-pointer and sliding window are the two patterns you should be able to whiteboard cold — they show up disguised in real frontend work constantly (infinite-scroll window management, debounced search ranges, diffing visible viewport rows).
- When a problem says "find the pair/subarray that…", your first question should be "is it sorted, and can I use two pointers or a hash-based complement lookup instead of nested loops?" — naming that decision tree out loud is the actual interview signal.
- Virtualized lists and windowed rendering (only rendering the DOM nodes currently in the viewport) are a *sliding window applied to the DOM* — the same "expand/contract the window, track state incrementally" logic, just with pixels instead of array indices.

## JavaScript Warm-Up Coding Questions (Part 1)

The ten most common "write it live" JS questions from screening rounds. Each has the expected answer plus the **follow-up** an interviewer usually asks next — the follow-up is where the actual signal is.

**Q1. Reverse a string** — `"hello"` → `"olleh"`
```js
function reverseString(str) {
  return str.split('').reverse().join('');
}
```
Split into a char array → `reverse()` → `join('')` back into a string. O(n).
*Follow-up:* `split('')` splits by UTF-16 code unit, so it breaks emoji and other surrogate pairs (`'😀'.split('')` gives two broken halves). Use `[...str].reverse().join('')` (spread iterates by code point) for Unicode-safe reversal.

**Q2. Remove duplicates from an array** — `[1,2,2,3,4,4,5]` → `[1,2,3,4,5]`
```js
const unique = [...new Set(arr)];
```
A `Set` stores only unique values; spread converts it back to an array. O(n), preserves first-occurrence order.
*Follow-up:* `Set` compares with SameValueZero, so `NaN` dedupes correctly but objects are compared **by reference** (two separate `{id:1}` objects both survive). For objects, dedupe by key: `[...new Map(arr.map(o => [o.id, o])).values()]`. The `arr.filter((x, i) => arr.indexOf(x) === i)` alternative works but is O(n²).

**Q3. Find the largest number** — `[10,25,5,90,40]` → `90`
```js
const largest = Math.max(...arr);
```
Spread turns the array into individual arguments; `Math.max()` returns the highest.
*Follow-up:* spread passes every element as a function argument, so very large arrays (~100k+ elements, engine-dependent) throw `RangeError: Maximum call stack size exceeded`. Use `arr.reduce((m, x) => (x > m ? x : m), -Infinity)` instead. Also: `Math.max()` on an empty array returns `-Infinity`, not an error.

**Q4. Check palindrome** — `"madam"` → `true`
```js
function isPalindrome(str) {
  const reversed = str.split('').reverse().join('');
  return str === reversed;
}
```
Reverse the string and compare it to the original; a palindrome reads the same forwards and backwards.
*Follow-up:* real-world inputs need normalizing first — `"A man, a plan, a canal: Panama"` fails as written. Lowercase and strip non-alphanumerics (`str.toLowerCase().replace(/[^a-z0-9]/g, '')`), then use **two pointers** from both ends: O(n) time, O(1) extra space, and it exits early on the first mismatch instead of building a reversed copy.

**Q5. Count character occurrences** — `"hello"` → `{ h: 1, e: 1, l: 2, o: 1 }`
```js
function countChars(str) {
  let result = {};
  for (let char of str) {
    if (result[char]) {
      result[char]++;
    } else {
      result[char] = 1;
    }
  }
  return result;
}
```
Loop over each character; if it's already a key, increment it, otherwise initialize it to 1.
*Follow-up:* the idiomatic one-liner body is `result[char] = (result[char] || 0) + 1;`. This frequency-counter shape is the base of anagram checks, first-non-repeating-character, and max-occurring-character (see the hashing patterns above); a `Map` is the better fit when you need guaranteed insertion order or non-string keys.

**Q6. Find the second largest number** — `[10,20,30,40]` → `30`
```js
const secondLargest = [...new Set(arr)].sort((a, b) => b - a)[1];
```
`Set` removes duplicates (so `[40,40,30]` still gives 30) → spread back to an array → sort descending → take index 1. If there are fewer than 2 distinct values, return `"Not Possible"` (index 1 would be `undefined`).
*Follow-ups:* (1) the `(a, b) => b - a` comparator is **mandatory** — plain `.sort()` sorts numbers as strings, so `[10, 9, 1].sort()` gives `[1, 10, 9]`. (2) Sorting is O(n log n); the expected optimization is a single O(n) pass:
```js
function secondLargest(arr) {
  let first = -Infinity, second = -Infinity;
  for (const n of arr) {
    if (n > first) { second = first; first = n; }
    else if (n > second && n < first) { second = n; }
  }
  return second === -Infinity ? 'Not Possible' : second;
}
```

**Q7. Find duplicate elements** — `[1,2,3,2,4,1]` → `[2, 1]` (order may vary)
```js
const duplicates = arr.filter((item, index) => arr.indexOf(item) !== index);
console.log([...new Set(duplicates)]);
```
`indexOf(item)` returns an element's *first* occurrence; if that differs from the current index, it's a repeat. `Set` then removes repeats from the duplicates list itself (a value appearing 3 times would otherwise be listed twice).
*Follow-up:* `indexOf` inside `filter` is O(n²). The O(n) version tracks what's been seen:
```js
const seen = new Set(), dupes = new Set();
for (const x of arr) seen.has(x) ? dupes.add(x) : seen.add(x);
[...dupes]; // [2, 1]
```

**Q8. Find the missing number** — `[1,2,3,5]` (numbers 1 to 5) → `4`
```js
const n = 5;                               // total numbers
const expected = (n * (n + 1)) / 2;        // sum of 1..n
const actual = arr.reduce((a, b) => a + b, 0);
console.log(expected - actual);            // 4
```
`n(n+1)/2` gives the sum of the first n natural numbers; the gap between expected and actual sums is the missing number. Only works when **exactly one** number is missing.
*Follow-ups:* derive `n` as `arr.length + 1` instead of hardcoding it. The classic alternative is XOR (XOR all of `1..n` with all array values; pairs cancel and the missing number remains), which avoids integer overflow in fixed-width languages. JS numbers are safe to 2⁵³, so overflow rarely matters here, but interviewers still ask. For *multiple* missing numbers, put the array in a `Set` and scan `1..n`.

**Q9. Sort an array without `sort()`** — `[5,2,8,1]` → `[1,2,5,8]`
```js
for (let i = 0; i < arr.length; i++) {
  for (let j = i + 1; j < arr.length; j++) {
    if (arr[i] > arr[j]) {
      [arr[i], arr[j]] = [arr[j], arr[i]];   // swap via destructuring
    }
  }
}
```
Outer loop picks each position; inner loop compares it against every later element and swaps if out of order. O(n²) — fine for small arrays. Note it **mutates** the original array.
*Follow-up / accuracy note:* this is commonly called "bubble sort" but is technically an **exchange sort** (it compares position `i` against all later positions). True bubble sort compares **adjacent** pairs and bubbles the largest value to the end each pass. Add a `swapped` flag to get the O(n) best case on already-sorted input:
```js
function bubbleSort(input) {
  const a = [...input];                      // don't mutate the caller's array
  for (let i = 0; i < a.length - 1; i++) {
    let swapped = false;
    for (let j = 0; j < a.length - 1 - i; j++) {
      if (a[j] > a[j + 1]) {
        [a[j], a[j + 1]] = [a[j + 1], a[j]];
        swapped = true;
      }
    }
    if (!swapped) break;                     // already sorted → stop early
  }
  return a;
}
```
If asked for something faster than O(n²), name merge sort (O(n log n), stable) or quicksort (O(n log n) average, O(n²) worst).

**Q10. Count vowels in a string** — `"javascript"` → `3` (a, a, i)
```js
function countVowels(str) {
  return str.match(/[aeiou]/gi)?.length || 0;
}
```
`[aeiou]` matches any vowel, `g` finds all occurrences, `i` makes it case-insensitive. `match()` returns an array of matches, so `.length` is the count.
*Follow-up:* `match()` returns `null` (not an empty array) when nothing matches — so `countVowels("rhythm")` would crash without the `?.` optional chaining, and `|| 0` turns the resulting `undefined` into `0`. A loop over a `Set` of vowels is the no-regex alternative if the interviewer rules out regex.

## Top 30 FAANG DSA Questions

The 30 problems from *Top 30 DSA Interview Questions (FAANG) in C++* (15 pages, two per page), regrouped by pattern. The Q numbers match the PDF so you can map back. Each entry gives the problem and the companies the source lists, the approach, a **JavaScript** solution, the original C++ in a collapsible block, complexity, a compact dry run, the source's FAANG tip, and the follow-up interviewers ask next. The JS is translated from the C++ with the same algorithm, and every solution was run in Node against the source's examples plus edge cases (193/193 checks pass). Where the source's code, dry run or complexity claim is wrong, a *Source note:* says what's wrong and what's right.

- **Duplicates in the source:** Q15 repeats Q12 (Floyd's cycle detection, same code), and Q23 repeats Q4 (product of array except self, O(n)-space variant). Q15 below is extended to the cycle-*start* follow-up so it isn't a copy.
- **Coverage gaps:** the source has no stack, binary-search, backtracking or DP problems (apart from Kadane), and only one graph problem. Use the pattern sections in this pillar for those.
- **C++ → JS traps that come up repeatedly below:**
  - `sort()` with no comparator compares as strings.
  - `/` doesn't truncate, so use `Math.floor`.
  - There's no built-in priority queue.
  - `Array.prototype.shift()` is O(n) inside a BFS loop.
  - `new Array(n).fill([])` puts one shared array in every slot.
  - C++ `int` overflow mostly disappears (integers are exact to 2⁵³), but `-0` can appear.

### Arrays & Hashing

**Q1. Two Sum** *(Amazon, Google, Meta)* — `nums = [2,7,11,15], target = 9` → `[0, 1]`

Given an integer array `nums` and an integer `target`, return the indices of the two numbers that add up to `target`.

- Walk the array once, keeping a `value → index` map of everything seen so far.
- At each element, look up its complement `target - nums[i]`. If it's in the map, return `[map.get(complement), i]`.
- Otherwise store `nums[i] → i`. Checking *before* storing is what stops an element pairing with itself.

```js
function twoSum(nums, target) {
  const seen = new Map();                   // value → index
  for (let i = 0; i < nums.length; i++) {
    const diff = target - nums[i];
    if (seen.has(diff)) return [seen.get(diff), i];
    seen.set(nums[i], i);
  }
  return [];                                // no solution
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> mp;

    for (int i = 0; i < nums.size(); i++) {
        int diff = target - nums[i];

        if (mp.count(diff))
            return {mp[diff], i};

        mp[nums[i]] = i;
    }

    return {};  // No solution
}
```

</details>

**Complexity:** O(N) time (one pass), O(N) space (the map).

```text
nums = [2, 7, 11, 15], target = 9
i=0  nums[i]=2  diff=7  map={}      → not found, store 2→0
i=1  nums[i]=7  diff=2  map={2→0}   → found → return [0, 1]
```

💡 *FAANG tip:* Always try to turn the O(N²) brute force (check every pair) into an O(N) hash-based solution.

*JS note:* use `Map.has()`, not `if (seen[diff])`. A complement stored at index `0` is falsy, so a truthiness check misses it. C++'s `mp.count()` tests existence, so it doesn't have this trap.

*See also:* the "complement lookup" bullet under **Arrays, Strings, Hashing & Two-Pointer / Sliding-Window Patterns** above. Subarray-sum-equals-K is the same idea extended to prefix sums.

*Follow-up:* "What if the array is sorted?" Use two pointers (`l = 0, r = n - 1`; move `l` right when the sum is too small and `r` left when it's too big) for O(1) extra space (Two Sum II). "Return all unique pairs": sort, run two pointers, and skip duplicate values on both sides. That leads straight into **3Sum**: fix one element, two-pointer the rest, O(N²). Sorting loses the original indices, so for the index version sort `[value, index]` pairs instead.

**Q7. Valid Anagram** *(Amazon, Microsoft, Adobe)* — `s = "listen", t = "silent"` → `true`

Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, otherwise `false`.

- Strings of different lengths can't be anagrams, so return `false` straight away.
- Count each letter of `s` into a 26-slot array, then decrement for each letter of `t`.
- It's an anagram exactly when every count ends at 0.

```js
function isAnagram(s, t) {
  if (s.length !== t.length) return false;
  const count = new Array(26).fill(0);      // C++: int count[26] = {0};
  for (const ch of s) count[ch.charCodeAt(0) - 97]++;   // 97 = 'a'
  for (const ch of t) count[ch.charCodeAt(0) - 97]--;
  for (let i = 0; i < 26; i++) {
    if (count[i] !== 0) return false;
  }
  return true;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
bool isAnagram(string s, string t) {
    if (s.size() != t.size()) return false;

    int count[26] = {0};

    for (char ch : s) count[ch - 'a']++;
    for (char ch : t) count[ch - 'a']--;

    for (int i = 0; i < 26; i++) {
        if (count[i] != 0) return false;
    }

    return true;
}
```

</details>

**Complexity:** O(N) time (each string traversed once), O(1) space (a fixed 26-slot array).

```text
s = "listen", t = "silent"
after s:  e:1 i:1 l:1 n:1 s:1 t:1   (every other letter 0)
after t:  every count back to 0     → return true
```

💡 *FAANG tip:* Anagrams have the same character frequencies. Sorting both strings is O(N log N), a hash map is O(N), and a fixed counting array is O(N) time with O(1) space, which makes counting the best choice.

*Source note:* the dry run's count row shows `l:2`, but "listen" has only one `l`, so it should be `l:1`.

*JS note:* `charCodeAt(0) - 97` assumes lowercase `a`–`z`, just like C++'s `ch - 'a'`. In C++, any other character writes outside the array, which is undefined behaviour. In JS it fails quietly instead: `count[-32]++` creates a stray `"-32"` property holding `NaN`, and the 0–25 check never looks at it. So `isAnagram("A", "B")` returns `true` (verified).

*See also:* the frequency-counter patterns under **Arrays, Strings, Hashing…** above, and Warm-Up **Q5** (count character occurrences), which uses the same counter shape.

*Follow-up:* "What if the input contains Unicode?" This is LeetCode's official follow-up. Use a `Map` keyed by character and iterate with `for...of`, which walks code points rather than UTF-16 units. Decide whether to normalise case and accents first (`str.normalize('NFC')`). **Group Anagrams** (Q10) is the usual next question.

**Q10. Group Anagrams** *(Google, Amazon, Meta)* — `["eat","tea","tan","ate","nat","bat"]` → `[["eat","tea","ate"],["tan","nat"],["bat"]]`

Given an array of strings, group the anagrams together. Any order is accepted.

- Anagrams share the same character-frequency vector, so use that vector as the hash key.
- Build the key from the 26 counts joined by a separator (`1#0#0#…`), then append the word to `map[key]`.
- Each map value is one group.

```js
function groupAnagrams(strs) {
  const mp = new Map();                     // frequency key → group
  for (const s of strs) {
    const freq = new Array(26).fill(0);
    for (const ch of s) freq[ch.charCodeAt(0) - 97]++;
    const key = freq.join('#');             // "1#0#0#0#1#…" — the separator is load-bearing
    if (!mp.has(key)) mp.set(key, []);
    mp.get(key).push(s);
  }
  return [...mp.values()];
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
vector<vector<string>> groupAnagrams(vector<string>& strs) {
    unordered_map<string, vector<string>> mp;

    for (string s : strs) {
        vector<int> freq(26, 0);
        for (char ch : s) freq[ch - 'a']++;

        string key = "";
        for (int i = 0; i < 26; ++i) {
            key += to_string(freq[i]) + '#';
        }
        mp[key].push_back(s);
    }

    vector<vector<string>> result;
    for (auto& p : mp) result.push_back(p.second);
    return result;
}
```

</details>

**Complexity:** O(N·K) time, where N = number of strings and K = average length. Strictly it's O(N·(K + 26)), because every key costs 26 steps however short the word is. O(N·K) space for the keys and groups.

```text
word   key (non-zero counts)   group
"eat"  a1 e1 t1                G1
"tea"  a1 e1 t1                G1
"tan"  a1 n1 t1                G2
"ate"  a1 e1 t1                G1
"nat"  a1 n1 t1                G2
"bat"  a1 b1 t1                G3
→ [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

💡 *FAANG tip:* Build a frequency-count key (O(K)) instead of sorting each string (O(K log K)). It performs better, and interviewers often ask for it as a follow-up.

*Source note:* the dry run shows sparse keys like `a#1 e#1 t#1`, but the code actually builds a dense 26-slot key (`"1#0#0#0#1#0#…#"`). On output order: C++ `unordered_map` returns the groups in unspecified order, while a JS `Map` keeps first-seen order, so the JS output matches the example exactly.

*JS note:* the `#` separator is load-bearing. Without it, the counts `[1, 11]` and `[11, 1]` both join to `"111…"`, and two words that aren't anagrams collide (there's a test for this).

*See also:* group anagrams under **Arrays, Strings, Hashing…** above, and Q7.

*Follow-up:* the simpler key is the sorted string, `[...s].sort().join('')`, at O(K log K). Default sort is fine here because you *want* code-unit order. For Unicode or uppercase input, the 26-slot key breaks, so switch to the sorted-string key or a `Map`-based count. Interviewers sometimes also ask about a prime-product key; it risks overflow in C++ and precision loss past 2⁵³ in JS.

**Q22. Top K Frequent Elements** *(Amazon, Google, Microsoft)* — `nums = [1,1,1,2,2,3], k = 2` → `[1, 2]`

Given an integer array `nums` and an integer `k`, return the `k` most frequent elements, in any order.

- Count frequencies with a hash map.
- Bucket sort by frequency: `bucket[f]` holds every number that appears exactly `f` times. No frequency can exceed `n`, so `n + 1` buckets are enough.
- Walk the buckets from high frequency to low, collecting numbers until you have `k`.

```js
function topKFrequent(nums, k) {
  const freq = new Map();
  for (const num of nums) freq.set(num, (freq.get(num) || 0) + 1);
  const n = nums.length;
  // NOT new Array(n + 1).fill([]) — that puts ONE shared array in every slot
  const bucket = Array.from({ length: n + 1 }, () => []);
  for (const [num, f] of freq) bucket[f].push(num);
  const result = [];
  for (let i = n; i >= 0 && result.length < k; i--) {   // high frequency → low
    for (const num of bucket[i]) {
      result.push(num);
      if (result.length === k) break;
    }
  }
  return result;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
vector<int> topKFrequent(vector<int>& nums, int k) {
    unordered_map<int, int> freq;
    for (int num : nums) freq[num]++;

    int n = nums.size();
    vector(vector<int>> bucket(n + 1);
    for (auto& p : freq) {
        int num = p.first, f = p.second;
        bucket[f].push_back(num);
    }

    vector<int> result;
    for (int i = n i >= 0 && result.size() < k; --i) {
        for (int num : bucket[i]) {
            result.push_back(num);
            if ((int)result.size() == k) break;
        }
    }
    return result;
}
```

</details>

**Complexity:** O(n) time (building the map, filling the buckets and collecting results are each linear), O(n) space (map plus buckets).

```text
nums = [1,1,1,2,2,3], k = 2
freq:    1→3  2→2  3→1
buckets: [0]:[] [1]:[3] [2]:[2] [3]:[1] [4]:[] [5]:[] [6]:[]
scan 6→0: take 1 (f=3), take 2 (f=2) → k reached → [1, 2]
```

💡 *FAANG tip:* When k is close to n, bucket sort beats a priority queue. For small k, use a size-k min-heap, which is O(n log k).

*Source note:* two typos stop the source from compiling: `vector(vector<int>> bucket` should be `vector<vector<int>>`, and `for (int i = n i >= 0` is missing a `;`. Separately, `result.size() < k` compares a `size_t` with an `int`, which triggers a signed/unsigned warning.

*JS note:* `new Array(n + 1).fill([])` is a classic bug. `fill` puts the *same* array object in every slot, so pushing into bucket 3 pushes into all of them (verified). Use `Array.from({ length: n + 1 }, () => [])`.

*See also:* top-K-frequent (bucket sort) under **Arrays, Strings, Hashing…** above, and bounded heaps under **Sorting, Searching, Heaps & Randomized Structures** below.

*Follow-up:*
- **"Do it with a heap":** keep a size-k min-heap keyed by frequency; the `MinHeap` from Q18 works.
- **"O(n) average without buckets":** run Quickselect on the unique values, ordered by frequency.
- **Top K Frequent *Words*:** adds a tie-break, so equal frequencies go in lexicographic order. The comparator becomes `(a, b) => fb - fa || (a < b ? -1 : 1)`. Don't reach for `localeCompare` unless the question asks for locale-aware order.
- **Streaming variants** (a "top 10 search terms" dashboard): the heap version is the one that survives.

**Q24. Longest Consecutive Sequence** *(Amazon, Google, Microsoft)* — `[100,4,200,1,3,2]` → `4` (`[1,2,3,4]`)

Given an unsorted integer array, return the length of the longest run of consecutive values. The source requires O(n).

- Put every number into a hash set.
- A number starts a run only if `num - 1` is *not* in the set.
- From each start, count upward while `num + 1` is in the set, and keep the longest run.

```js
function longestConsecutive(nums) {
  if (nums.length === 0) return 0;
  const st = new Set(nums);
  let longest = 0;
  for (const num of st) {                   // iterate the Set, not nums (duplicates would re-scan runs)
    if (!st.has(num - 1)) {                 // only start counting at the beginning of a run
      let curr = num, len = 1;
      while (st.has(curr + 1)) {
        curr++;
        len++;
      }
      longest = Math.max(longest, len);
    }
  }
  return longest;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
int longestConsecutive(vector<int>& nums) {
    if (nums.empty()) return 0;
    unordered_set<int> st(nums.begin(), nums.end());
    int longest = 0;

    for (int num : st) {
        // check if num is the start of a sequence
        if (st.find(num - 1) == st.end()) {
            int curr = num, len = 1;
            // expand the sequence
            while (st.find(curr + 1) != st.end()) {
                curr++;
                len++;
            }
            longest = max(longest, len);
        }
    }
    return longest;
}
```

</details>

**Complexity:** O(n) time. The inner `while` only runs from run starts, so each element is visited at most twice: once in the outer loop and once while its run is expanded. O(n) space for the set.

```text
set = {100, 4, 200, 1, 3, 2}
100: 99 not in set  → start → [100]      len 1
4:   3 IS in set    → skip (not a start)
200: 199 not in set → start → [200]      len 1
1:   0 not in set   → start → 1,2,3,4    len 4 ← max
3:   2 in set → skip      2: 1 in set → skip
→ 4
```

💡 *FAANG tip:* Only start counting from numbers that have no predecessor (`num - 1`). That guarantees each number is processed at most twice.

*Source note:* the dry-run row for `4` says "Yes (3 not in set)". But 3 *is* in the set, so 4 isn't a start; only 100, 200 and 1 start runs. In C++, `num - 1` and `curr + 1` overflow at `INT_MIN`/`INT_MAX`, which is undefined behaviour. JS numbers don't have this problem.

*JS note:* iterate the **Set**, not the original array, just like the C++ does. If you loop over the array instead, input like `[1,1,1,…,2,3,…]` makes every duplicate `1` re-walk the whole run, and the time degrades to O(n²).

*See also:* longest consecutive sequence under **Arrays, Strings, Hashing…** above.

*Follow-up:* "Why not sort?" Sorting is O(n log n), and it needs a numeric comparator plus duplicate-skipping. "Return the sequence itself": record the best start, then build `Array.from({ length: best }, (_, i) => start + i)`. Union-Find is a less common alternative that interviewers sometimes ask about.

### Greedy, Kadane & Prefix/Suffix Products

**Q2. Best Time to Buy and Sell Stock** *(Amazon, Microsoft)* — `prices = [7,1,5,3,6,4]` → `5`

Given `prices[i]`, the stock price on day `i`, return the maximum profit from one buy followed by one later sell, or 0 if no profit is possible.

- Track the minimum price seen so far, which is the best day to have bought.
- Each day, profit = today's price − that minimum. Keep the maximum.
- The code updates the minimum *before* computing profit. That's safe, because buying and selling on the same day gives 0.

```js
function maxProfit(prices) {
  let minPrice = Infinity;                  // C++: INT_MAX
  let maxProfit = 0;
  for (const price of prices) {
    minPrice = Math.min(minPrice, price);   // cheapest buy day so far
    maxProfit = Math.max(maxProfit, price - minPrice);   // best sell today
  }
  return maxProfit;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
int maxProfit(vector<int>& prices) {
    int minPrice = INT_MAX;
    int maxProfit = 0;

    for (int price : prices) {
        minPrice = min(minPrice, price);
        maxProfit = max(maxProfit, price - minPrice);
    }

    return maxProfit;
}
```

</details>

**Complexity:** O(N) time (one pass), O(1) space.

```text
day  price  minPrice  profit  maxProfit
0    7      7         0       0
1    1      1         0       0
2    5      1         4       4
3    3      1         2       4
4    6      1         5       5   ← buy day 1 @1, sell day 4 @6
5    4      1         3       5
```

💡 *FAANG tip:* Greedy is powerful when the best local choice at each step also gives the best overall answer.

*See also:* this is Kadane in disguise: max profit = the maximum subarray sum of the daily differences `prices[i] - prices[i-1]` (see Q3, and the Kadane bullet under **Arrays, Strings, Hashing…** above).

*Follow-up:* the "Stock" series is a ladder of follow-ups:
- **II (unlimited transactions):** sum every positive day-to-day difference.
- **III/IV (at most k transactions):** DP over (day, transactions left, holding?).
- **With cooldown or a transaction fee:** a small state machine (hold / sold / rest).
- **Return the actual days:** record the index whenever `minPrice` or `maxProfit` changes.

**Q3. Maximum Subarray (Kadane's Algorithm)** *(Amazon, Google, Microsoft)* — `[-2,1,-3,4,-1,2,1,-5,4]` → `6` (subarray `[4,-1,2,1]`)

Given an integer array, find the contiguous subarray with the largest sum and return that sum.

- Keep a running sum and add each element to it.
- Update the best sum seen so far *before* doing anything else.
- If the running sum drops below 0, reset it to 0. A negative prefix can only drag down whatever comes next ("extend or restart").

```js
function maxSubArray(nums) {
  let currentSum = 0;
  let maxSum = -Infinity;                   // C++: INT_MIN
  for (const x of nums) {
    currentSum += x;
    maxSum = Math.max(maxSum, currentSum);  // record BEFORE resetting → all-negative input works
    if (currentSum < 0) currentSum = 0;     // a negative running sum only hurts: restart
  }
  return maxSum;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

int maxSubArray(vector<int>& nums) {
    int currentSum = 0;
    int maxSum = INT_MIN;

    for (int x : nums) {
        currentSum += x;
        maxSum = max(maxSum, currentSum);

        if (currentSum < 0)
            currentSum = 0;
    }

    return maxSum;
}
```

</details>

**Complexity:** O(N) time (one pass), O(1) space.

```text
i       0   1   2   3   4   5   6   7   8
x      -2   1  -3   4  -1   2   1  -5   4
cur    -2   1  -2   4   3   5   6   1   5   (after adding x; reset to 0 when < 0)
max    -2   1   1   4   4   5   6   6   6
reset   ✓       ✓
→ 6, subarray i=3..6 = [4, -1, 2, 1]
```

💡 *FAANG tip:* Kadane's algorithm is a must for subarray problems. Think "extend or restart" at every step.

*Source note:* the source's dry-run table is garbled. Its index row skips 4. Its `nums` row has only 8 values and ends `2, -1, 4` instead of `2, 1, -5, 4`. Its `currentSum`/`maxSum` rows don't match the code either; for example, `maxSum` becomes 5 at the `-1`. One bar in the visualisation is also labelled `6` where it should be `1`. The code and the answer (6) are correct, and the table above is the actual trace.

Two edge cases:
- **All-negative input:** updating `maxSum` *before* the reset is what makes it return the least-negative element rather than 0.
- **Empty array:** returns `-Infinity` (C++: `INT_MIN`), so guard it if the caller cares.

In C++, `currentSum` can overflow `int` on large inputs; JS numbers don't.

*See also:* the Kadane bullet under **Arrays, Strings, Hashing…** above, which covers the max-*product* variant (track both a min and a max, and swap them on a negative).

*Follow-up:*
- **"Return the subarray":** set `start = i + 1` whenever you reset, and snapshot `[start, i]` whenever `max` improves.
- **"Maximum circular subarray":** `max(kadaneMax, total - kadaneMin)`, but if every element is negative, return `kadaneMax`.
- **"Divide-and-conquer version?"** It's O(N log N). Interviewers ask it to check you know Kadane is strictly better.

**Q4. Product of Array Except Self** *(Google, Amazon, Meta)* — `[1,2,3,4]` → `[24,12,8,6]`

Return `result` where `result[i]` is the product of every element except `nums[i]`, without using division and in O(n) time.

- Pass 1, left to right: write the running product of everything *left* of `i` into `result[i]`.
- Pass 2, right to left: multiply `result[i]` by the running product of everything *right* of `i`.
- Because nothing is divided, zeros are handled naturally.

```js
function productExceptSelf(nums) {
  const n = nums.length;
  const result = new Array(n).fill(1);
  let leftProduct = 1;
  for (let i = 0; i < n; i++) {             // pass 1: product of everything LEFT of i
    result[i] = leftProduct;
    leftProduct *= nums[i];
  }
  let rightProduct = 1;
  for (let i = n - 1; i >= 0; i--) {        // pass 2: multiply in everything RIGHT of i
    result[i] *= rightProduct;
    rightProduct *= nums[i];
  }
  return result;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
vector<int> productExceptSelf(vector<int>& nums) {
    int n = nums.size();
    vector<int> result(n, 1);

    int leftProduct = 1;
    for (int i = 0; i < n; ++i) {
        result[i] = leftProduct;
        leftProduct *= nums[i];
    }

    int rightProduct = 1;
    for (int i = n - 1; i >= 0; --i) {
        result[i] *= rightProduct;
        rightProduct *= nums[i];
    }

    return result;
}
```

</details>

**Complexity:** O(N) time (two passes), O(1) extra space. By LeetCode convention the output array doesn't count.

```text
nums              1    2    3    4
left  (before i)  1    1    2    6
right (after i)  24   12    4    1
result = L × R   24   12    8    6
e.g. i=2: product of [1,2] = 2, product of [4] = 4 → 2 × 4 = 8
```

💡 *FAANG tip:* Look for patterns that avoid division and still achieve O(n) time.

*JS note:* with a zero and negatives you can get **`-0`**. `[-1,1,0,-3,3]` returns `[-0, 0, 9, -0, 0]` (verified). Because `-0 === 0` is `true`, ordinary comparisons pass. But `Object.is`, Node's `assert.deepStrictEqual` and Jest's `toBe` all treat `-0` and `0` as different, and `console.log` prints `-0`. Normalise with `x || 0` if it matters. In C++ the running products can overflow `int` on large inputs (LeetCode guarantees they fit); JS integers are exact up to 2⁵³.

*See also:* the prefix/suffix bullet under **Arrays, Strings, Hashing…** above, and **Q23**, which is the same problem using explicit `left[]`/`right[]` arrays.

*Follow-up:* "What if division were allowed?" Count the zeros:
- **Two or more zeros:** every result is 0.
- **Exactly one zero:** only that index is non-zero, holding the product of the rest.
- **No zeros:** each result is `total / nums[i]`.

Working through those cases is the real test. "Why not just divide?" Zeros break it, and in C++ the total product can overflow.

**Q23. Product of Array Except Self (prefix & suffix arrays)** *(Amazon, Google, Microsoft)* — `[1,2,3,4]` → `[24,12,8,6]`

This is the same problem as Q4. The source repeats it with the more explicit three-array version, which is easier to explain first before optimising.

- `left[i]` = product of everything left of `i`, with `left[0] = 1`.
- `right[i]` = product of everything right of `i`, with `right[n-1] = 1`.
- `answer[i] = left[i] * right[i]`.

```js
function productExceptSelfPrefixSuffix(nums) {
  const n = nums.length;
  const left = new Array(n).fill(1);
  const right = new Array(n).fill(1);
  const answer = new Array(n).fill(1);
  for (let i = 1; i < n; i++) left[i] = left[i - 1] * nums[i - 1];        // build left products
  for (let i = n - 2; i >= 0; i--) right[i] = right[i + 1] * nums[i + 1]; // build right products
  for (let i = 0; i < n; i++) answer[i] = left[i] * right[i];             // combine
  return answer;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
vector<int> productExceptSelf(vector<int>& nums) {
    int n = nums.size();
    vector<int> left(n, 1), right(n, 1), answer(n, 1);

    // Build left products
    for (int i = 1; i < n; i++)
        left[i] = left[i - 1] * nums[i - 1];

    // Build right products
    for (int i = n - 2; i >= 0; i--)
        right[i] = right[i + 1] * nums[i + 1];

    // Build answer
    for (int i = 0; i < n; i++)
        answer[i] = left[i] * right[i];

    return answer;
}
```

</details>

**Complexity:** O(n) time (three linear passes), O(n) space for `left[]`, `right[]` and `answer[]`. You can drop to O(1) extra space by reusing the output array as `left[]` and folding `right` into a running variable, which is exactly Q4.

```text
index    0          1          2        3
left     1          1          2        6       (1, 1·1, 1·2, 2·3)
right    24         12         4        1       (2·3·4, 3·4, 4, 1)
answer   1·24=24    1·12=12    2·4=8    6·1=6
```

💡 *FAANG tip:* Avoid division by using prefix and suffix products. This can be optimised to O(1) extra space by storing the answer in place of `left[]` or `right[]`.

*Source note:* this duplicates Q4. In an interview, present this version first as "the obvious one", then optimise it to Q4 out loud. Showing that step is the interview signal.

*Follow-up:* same as Q4. You may also get "can you do it in one pass?" Yes: fill from both ends at once with two running products (`res[i] *= L; L *= nums[i]; res[n-1-i] *= R; R *= nums[n-1-i]`). It's still O(n), so it's really a check on whether you know the complexity doesn't change.

### Two Pointers & Sliding Window

**Q6. Rotate Array** *(Amazon, Microsoft)* — `nums = [1,2,3,4,5,6,7], k = 3` → `[5,6,7,1,2,3,4]`

Rotate the array to the right by `k` steps, in place, where `k` is non-negative.

- Reduce `k` with `k % n`, because rotating by `n` is a no-op.
- Reverse the whole array, then reverse the first `k` elements, then reverse the remaining `n − k`.
- Why it works: the full reversal moves the last `k` elements to the front, but backwards. The two partial reversals put each block back in order.

```js
function rotate(nums, k) {
  const n = nums.length;
  if (n === 0) return;                      // C++ would evaluate k % 0 (undefined behaviour)
  k = k % n;                                // handle k > n
  reverseRange(nums, 0, n - 1);             // Step 1: reverse everything
  reverseRange(nums, 0, k - 1);             // Step 2: reverse the first k
  reverseRange(nums, k, n - 1);             // Step 3: reverse the remaining n - k
}

function reverseRange(nums, l, r) {
  while (l < r) {
    [nums[l], nums[r]] = [nums[r], nums[l]];
    l++;
    r--;
  }
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
void reverse(vector<int>& nums, int l, int r) {
    while (l < r) swap(nums[l++], nums[r--]);
}

void rotate(vector<int>& nums, int k) {
    int n = nums.size();
    k = k % n;                   // handle k > n

    reverse(nums, 0, n-1);       // Step 1
    reverse(nums, 0, k-1);       // Step 2
    reverse(nums, k, n-1);       // Step 3
}
```

</details>

**Complexity:** O(N) time (the three reversals touch each element at most twice), O(1) space.

```text
nums = [1,2,3,4,5,6,7], k = 3
reverse all        → 7 6 5 4 3 2 1
reverse first k=3  → 5 6 7 | 4 3 2 1
reverse last n-k=4 → 5 6 7 | 1 2 3 4   ✓
```

💡 *FAANG tip:* The reverse algorithm is easy to implement and runs in O(N) time with O(1) space.

*Source note:* for an empty array, the C++ evaluates `k % 0`, which is undefined behaviour (usually a crash). LeetCode guarantees `n ≥ 1`, but the JS version guards against it anyway. Without the guard, JS's `k % 0` is `NaN`, and the loops would silently do nothing.

*JS note:* like the C++ `void` function, this mutates `nums` and returns `undefined`. Writing `const r = rotate(a, 3)` and getting `undefined` is a common live-coding slip. The one-liner `nums.unshift(...nums.splice(-k))` also works for `k ≤ n`, but it allocates and spreads the arguments, which hits the argument-count limit on huge arrays. It's also wrong when `k > n` unless you reduce `k` first: rotating `[1,2,3]` by 5 leaves it unchanged instead of giving `[2,3,1]` (verified).

*See also:* the three-step reversal as a readability-vs-micro-optimisation trade-off, under **Complexity Analysis & Trade-offs** above.

*Follow-up:*
- **"Rotate left?"** Rotate right by `n − k`.
- **"Use an extra array?"** `res[(i + k) % n] = nums[i]`. It's O(n) space, but simpler to prove correct.
- **"Another O(1)-space method?"** Cyclic replacements (juggling): move each element straight to `(i + k) % n`, following `gcd(n, k)` cycles.
- **2D version:** rotating a matrix 90° is transpose, then reverse each row.

**Q8. Longest Substring Without Repeating Characters** *(Amazon, Google, Microsoft)* — `"abcabcbb"` → `3` (`"abc"`)

Given a string, return the length of the longest substring with no repeated characters.

- Keep a sliding window `[left, right]` and a map of each character's last-seen index.
- Expand `right` one character at a time.
- If the new character was last seen *inside* the window (`last ≥ left`), jump `left` to one past that position.
- After each step, record `right − left + 1`.

```js
function lengthOfLongestSubstring(s) {
  const last = new Map();                   // char → last index seen
  let left = 0, maxLen = 0;
  for (let right = 0; right < s.length; right++) {
    const ch = s[right];
    if (last.has(ch) && last.get(ch) >= left) {
      left = last.get(ch) + 1;              // jump past the previous copy (only if inside the window)
    }
    last.set(ch, right);
    maxLen = Math.max(maxLen, right - left + 1);
  }
  return maxLen;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
int lengthOfLongestSubstring(string s) {
    unordered_map<char, int> last;
    int left = 0, maxLen = 0;

    for (int right = 0; right < s.size(); right++) {
        char ch = s[right];

        if (last.count(ch) && last[ch] >= left)
            left = last[ch] + 1;

        last[ch] = right;
        maxLen = max(maxLen, right - left + 1);
    }

    return maxLen;
}
```

</details>

**Complexity:** O(N) time, O(min(N, K)) space, where K = the size of the character set.

```text
s = "abcabcbb"
r  ch  left  window  max
0  a   0     a       1
1  b   0     ab      2
2  c   0     abc     3
3  a   1     bca     3   (a last at 0 ≥ left → left = 1)
4  b   2     cab     3
5  c   3     abc     3
6  b   5     cb      3   (b last at 4 → left = 5)
7  b   7     b       3   (b last at 6 → left = 7)
→ 3
```

💡 *FAANG tip:* Use a sliding window with a hash map that tracks each character's last index. This pattern shows up in many string problems.

*Source note:*
- **Last dry-run row:** it shows `left = 8`, but it should be `7`. The window `"b"` shown next to it is correct.
- **"We visit each character at most twice":** that's true of the Set-and-shrink variant, where `left` walks forward one step at a time. This jump-`left` version touches each character exactly once.
- **"At most 256 for ASCII":** ASCII has 128 characters; 256 is extended ASCII.

*JS note:* the `last.get(ch) >= left` check is essential. Without it, `"abba"` jumps `left` *backwards* to the stale `a` and returns 3 instead of 2 (this case is in the tests). Also, `s[right]` indexes UTF-16 code units, so an emoji counts as two "characters". Spread with `[...s]` first if the question is about user-visible characters.

*See also:* the variable-size sliding-window bullet under **Arrays, Strings, Hashing…** above. Virtualised lists apply the same "expand and contract a window" idea to the DOM.

*Follow-up:*
- **Longest substring with at most K distinct characters:** keep a count map, and shrink while `map.size > k`.
- **Longest repeating character replacement:** shrink while `windowLen − maxFreq > k`.
- **Minimum window substring:** expand until the window is valid, then shrink to minimise it.
- **Return the substring itself:** track `bestStart` alongside the length.

**Q9. Longest Palindromic Substring** *(Amazon, Microsoft, Apple)* — `"babad"` → `"bab"` (`"aba"` is also valid)

Given a string `s`, return its longest palindromic substring.

- Every palindrome mirrors around a centre. There are 2n − 1 possible centres: each character (odd lengths) and each gap between characters (even lengths).
- From each centre, expand outwards while both ends match.
- Keep the longest palindrome found.

```js
function expandAroundCenter(s, l, r) {
  while (l >= 0 && r < s.length && s[l] === s[r]) {
    l--;
    r++;
  }
  return s.slice(l + 1, r);                 // C++ s.substr(l + 1, r - l - 1) takes a LENGTH; slice takes an END
}

function longestPalindrome(s) {
  if (s.length <= 1) return s;
  let ans = '';
  for (let i = 0; i < s.length; i++) {
    const odd = expandAroundCenter(s, i, i);        // odd length: centre is one char
    const even = expandAroundCenter(s, i, i + 1);   // even length: centre is between two chars
    if (odd.length > ans.length) ans = odd;
    if (even.length > ans.length) ans = even;
  }
  return ans;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
string expandAroundCenter(const string& s, int l, int r) {
    while (l >= 0 && r < s.size() && s[l] == s[r]) {
        l--;
        r++;
    }
    return s.substr(l + 1, r - l - 1);
}

string longestPalindrome(string s) {
    if (s.size() <= 1) return s;
    string ans = "";
    for (int i = 0; i < s.size(); ++i) {
        string odd = expandAroundCenter(s, i, i);
        string even = expandAroundCenter(s, i, i + 1);
        if (odd.size() > ans.size()) ans = odd;
        if (even.size() > ans.size()) ans = even;
    }
    return ans;
}
```

</details>

**Complexity:** O(n²) time, because each of the ~2n centres can expand up to O(n). For space, see the source note.

```text
s = "babad"   centre → palindrome   (longest so far)
(0,0) odd  → "b"                    ("b")
(0,1) even → ""
(1,1) odd  → "bab"  s[0]=b = s[2]=b ("bab")
(1,2) even → ""
(2,2) odd  → "aba"  same length, only a strictly longer one replaces "bab"
(2,3) even → ""
(3,3) odd  → "a"    s[2]=b ≠ s[4]=d
(3,4) even → ""
(4,4) odd  → "d"
→ "bab"
```

💡 *FAANG tip:* Expand Around Center is a very important pattern. Remember that every palindrome has a centre, odd or even. The approach is simple, space-optimised and an interview favourite.

*Source note:*
1. **Mislabelled centres:** the dry-run table and visualisation give `(1,1) → "aba"`, `(2,2) → "bab"` and `(3,3) → "aba"`. The actual results are `"bab"`, `"aba"` and `"a"`, and the code returns `"bab"` (verified).
2. **Space is O(n) as written, not O(1):** every `expandAroundCenter` call returns a new substring, and `ans` holds a copy. For true O(1) extra space, have the helper return the expanded bounds, track `(start, maxLen)`, and slice once at the end.

*JS note:* C++ `s.substr(pos, len)` takes a **length**, while JS `slice(start, end)` and `substring(start, end)` take an **end index**. That's why the JS uses `s.slice(l + 1, r)`. Carrying `substr(l + 1, r - l - 1)` straight over into `slice` is a classic bug, and JS's own `substr` is deprecated.

*Follow-up:*
- **"Better than O(n²)?"** Manacher's algorithm runs in O(n). Name it; you're rarely expected to code it.
- **Palindromic Substrings** (LC 647, count them): the same expand loop, adding 1 for each successful expansion.
- **DP table:** O(n²) time *and* O(n²) space, so expand-around-centre beats it.
- **Longest palindromic *subsequence*:** genuinely a 2D DP problem (see **Dynamic Programming** below).

**Q21. Trapping Rain Water** *(Amazon, Google, Microsoft)* — `[0,1,0,2,1,0,1,3,2,1,2,1]` → `6`

Given bar heights, each bar 1 wide, compute how much water is trapped after rain.

- The water above bar `i` is `min(maxLeft, maxRight) − height[i]`.
- Use two pointers from both ends, tracking `leftMax` and `rightMax`.
- Always move the side with the *smaller* height. That side's max is guaranteed to be the binding limit, because the other side already has a wall at least as tall.

```js
function trap(height) {
  let left = 0, right = height.length - 1;
  let leftMax = 0, rightMax = 0;
  let water = 0;
  while (left < right) {
    if (height[left] <= height[right]) {
      // a wall ≥ height[left] exists on the right, so leftMax alone bounds this cell
      if (height[left] >= leftMax) leftMax = height[left];
      else water += leftMax - height[left];
      left++;
    } else {
      if (height[right] >= rightMax) rightMax = height[right];
      else water += rightMax - height[right];
      right--;
    }
  }
  return water;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
int trap(vector<int>& height) {
    int n = height.size();
    int left = 0, right = n - 1;
    int leftMax = 0, rightMax = 0;
    int water = 0;

    while (left < right) {
        if (height[left] <= height[right]) {
            if (height[left] >= leftMax)
                leftMax = height[left];
            else
                water += leftMax - height[left];
            left++;
        } else {
            if (height[right] >= rightMax)
                rightMax = height[right];
            else
                water += rightMax - height[right];
            right--;
        }
    }
    return water;
}
```

</details>

**Complexity:** O(n) time (single pass), O(1) space.

```text
height = [0,1,0,2,1,0,1,3,2,1,2,1]
L  R   h[L] h[R] move        leftMax rightMax  +water total
0  11  0    1    left        0       0         0      0
1  11  1    1    left (tie)  1       0         0      0
2  11  0    1    left        1       0         1      1
3  11  2    1    right       1       1         0      1
3  10  2    2    left (tie)  2       1         0      1
4  10  1    2    left        2       1         1      2
5  10  0    2    left        2       1         2      4
6  10  1    2    left        2       1         1      5
7  10  3    2    right       2       2         0      5
7  9   3    1    right       2       2         1      6
7  8   3    2    right       2       2         0      6   → L meets R, answer 6
```

💡 *FAANG tip:* The key insight is that the water level at any index depends on the minimum of the max heights to its left and right. Two pointers eliminate the need for extra arrays.

*Source note:* the source's dry-run table doesn't follow its own code. On a tie (`height[left] <= height[right]`), the code moves **left**, but the table's rows 1–2 move right, which throws off its `leftMax`/`rightMax` columns. The answer (6) is correct, and the table above is the real trace (the solution also matches a brute-force check on 300 random inputs). The problem statement's `height[1]` is a typo for `height[]`.

*See also:* the two-pointer bullet under **Arrays, Strings, Hashing…** above, and the monotonic-stack approach under **Stacks, Queues & Monotonic Structures** below.

*Follow-up:*
- **"Explain it with arrays first":** build `prefixMax[]` and `suffixMax[]`, then sum `min(prefixMax[i], suffixMax[i]) − h[i]`. It's O(n) space but easier to prove, and it's the natural stepping stone to two pointers.
- **Stack version:** a monotonic decreasing stack computes the water layer by layer.
- **Trapping Rain Water II** (2D grid): run a min-heap BFS inwards from the border.
- **Don't confuse it with Container With Most Water:** that also uses two pointers, but it maximises `min(h[l], h[r]) · (r − l)` over just two walls.

### Intervals (Sort + Sweep)

**Q5. Merge Intervals** *(Amazon, Google, Meta)* — `[[1,3],[2,6],[8,10],[15,18]]` → `[[1,6],[8,10],[15,18]]`

Merge all overlapping `[start, end]` intervals and return the non-overlapping intervals that cover the whole input.

- Sort the intervals by start time.
- Keep a `current` interval. If the next interval starts at or before `current` ends (`next.start <= current.end`), they overlap, so extend `current.end = max(current.end, next.end)`.
- Otherwise, push `current` to the result and start a new one from the next interval. At the end, push the last `current`.

```js
function mergeIntervals(intervals) {
  if (intervals.length === 0) return [];
  // numeric comparator is mandatory: default sort() compares "15,18" < "2,6" as strings
  const sorted = [...intervals].sort((a, b) => a[0] - b[0]);
  const result = [];
  let current = [...sorted[0]];             // copy — C++ copies the vector, JS would alias the input
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i][0] <= current[1]) {
      current[1] = Math.max(current[1], sorted[i][1]);   // overlap → extend
    } else {
      result.push(current);                 // gap → close the current interval
      current = [...sorted[i]];
    }
  }
  result.push(current);                     // don't forget the last one
  return result;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
vector<vector<int>> merge(vector<vector<int>>& intervals) {
    if (intervals.empty()) return {};

    sort(intervals.begin(), intervals.end());
    vector<vector<int>> result;
    vector<int> current = intervals[0];

    for (int i = 1; i < intervals.size(); ++i) {
        if (intervals[i][0] <= current[1]) {
            current[1] = max(current[1], intervals[i][1]);
        } else {
            result.push_back(current);
            current = intervals[i];
        }
    }
    result.push_back(current);

    return result;
}
```

</details>

**Complexity:** O(N log N) time, since the sort dominates and the sweep itself is O(N). O(N) space for the result, plus whatever the sort uses internally.

```text
sorted: [1,3] [2,6] [8,10] [15,18]
[1,3]    → current [1,3]            result []
[2,6]    → 2 ≤ 3 overlap → [1,6]    result []
[8,10]   → 8 > 6 → push [1,6]       result [[1,6]]
[15,18]  → 15 > 10 → push [8,10]    result [[1,6],[8,10]]
end      → push [15,18]             result [[1,6],[8,10],[15,18]]
```

💡 *FAANG tip:* Sorting is the key. Once the intervals are sorted, merging becomes a simple linear scan.

*JS note:* two traps here don't exist in the C++:
- **The comparator.** `intervals.sort()` with no comparator turns each `[a, b]` into the string `"a,b"` and sorts them lexicographically. For example, `[[8,10],[15,18],[2,6],[1,3]].sort()` gives `[[1,3],[15,18],[2,6],[8,10]]` (verified), and the merge then silently returns garbage. Always pass `(a, b) => a[0] - b[0]`.
- **Aliasing.** In C++, `vector<int> current = intervals[i]` makes a *copy*. In JS, `current = intervals[i]` points at the input array itself, so `current[1] = …` would mutate the caller's data. That's why the JS copies with `[...sorted[i]]`. For the same reason, the JS sorts a copy of the input, whereas the C++ sorts the caller's vector in place.

*See also:* the interval-sweep bullet (merge, insert, meeting rooms) under **Intervals, Caching & Frontend-Applied System Design Patterns** below.

*Follow-up:*
- **Insert Interval:** the input is already sorted and disjoint, so no sort is needed. Do an O(n) three-phase sweep: intervals entirely before the new one, overlapping intervals merged into it, then intervals entirely after.
- **Meeting Rooms II:** count the maximum overlap, either with a min-heap of end times or by sweeping the sorted starts and ends with two pointers.
- **"Do `[1,4]` and `[4,5]` overlap?"** Clarify the boundary rule. Using `<=` merges intervals that only touch, and LeetCode counts that as overlapping. Calendar-style problems with half-open intervals don't.
- **Streaming intervals:** keep them in a balanced BST or another sorted structure keyed by start.

### Linked Lists

All the linked-list answers below share this node class, the JS equivalent of the source's `struct ListNode`:

```js
class ListNode {
  constructor(val = 0, next = null) {
    this.val = val;
    this.next = next;
  }
}
```

**Q11. Reverse Linked List** *(Amazon, Google, Microsoft)* — `1→2→3→4→5` → `5→4→3→2→1`

Reverse a singly linked list and return the new head.

- Walk the list with three pointers: `prev`, `curr` and `next`.
- At each node, save `next`, point `curr.next` back at `prev`, then advance both.
- When `curr` falls off the end, `prev` is the new head.

```js
function reverseList(head) {
  let prev = null;
  let curr = head;
  while (curr !== null) {
    const next = curr.next;                 // save before overwriting
    curr.next = prev;                       // flip the pointer
    prev = curr;
    curr = next;
  }
  return prev;                              // new head
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(NULL) {}
};

ListNode* reverseList(ListNode* head) {
    ListNode* prev = NULL;
    ListNode* curr = head;
    while (curr != NULL) {
        ListNode* next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;  // New head
}
```

</details>

**Complexity:** O(N) time (each node visited once), O(1) space (three pointers).

```text
start:  prev=null  curr=1
step 1: next=2     1→null             prev=1 curr=2
step 2: next=3     2→1→null           prev=2 curr=3
step 3: next=4     3→2→1→null         prev=3 curr=4
step 4: next=5     4→3→2→1→null       prev=4 curr=5
step 5: next=null  5→4→3→2→1→null     prev=5 curr=null → return 5
```

💡 *FAANG tip:* This is a fundamental linked-list problem and extremely common in coding interviews. Practise until you can do it in your sleep.

*Source note:* the dry run's "Original List" box shows `1→2→3→4`, but its table and answer use five nodes (`…→5`). The trace above uses five nodes throughout.

*See also:* the reversal primitive under **Linked Lists** below, which covers reversing a sublist, reordering and the palindrome check.

*Follow-up:*
- **"Recursive version?"** `if (!head || !head.next) return head; const h = reverseList(head.next); head.next.next = head; head.next = null; return h;` (verified). It uses an O(n) call stack, and Node overflows at roughly 12k frames for a trivial function, so the iterative version is the production answer.
- **Reverse Linked List II:** reverse only positions `left` to `right`.
- **Reverse Nodes in k-Group:** reverse each block of k nodes.
- **Palindrome Linked List:** find the middle, reverse the second half, then compare the halves.

**Q12. Linked List Cycle** *(Amazon, Google, Microsoft)* — `1→2→3→4→(back to 2)` → `true`

Given the head of a linked list, return `true` if it contains a cycle.

- Move a slow pointer one step and a fast pointer two steps at a time (Floyd's tortoise and hare).
- If there's a cycle, fast eventually laps slow and they land on the same node.
- If `fast` or `fast.next` hits `null`, the list ends, so there's no cycle.

```js
function hasCycle(head) {
  if (!head || !head.next) return false;
  let slow = head;
  let fast = head;
  while (fast && fast.next) {
    slow = slow.next;                       // 1 step
    fast = fast.next.next;                  // 2 steps
    if (slow === fast) return true;         // same NODE (reference), not same value
  }
  return false;                             // fast reached null → no cycle
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(NULL) {}
};

bool hasCycle(ListNode* head) {
    if (!head || !head->next) return false;

    ListNode* slow = head;
    ListNode* fast = head;

    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;
    }
    return false;  // No cycle
}
```

</details>

**Complexity:** O(N) time, O(1) space.

```text
No cycle: 1→2→3→4→null          Cycle: 1→2→3→4→(2)
step  slow  fast                 step  slow  fast
0     1     1                    0     1     1
1     2     3                    1     2     3
2     3     null → false         2     3     2
                                 3     4     4   → meet → true
```

💡 *FAANG tip:* Floyd's tortoise-and-hare algorithm is the most optimal solution, with O(1) space.

*Source note:* the claim "each node is visited at most once" isn't accurate: inside a cycle, `fast` can lap it several times before meeting `slow`. The bound is still O(N). `slow` enters the cycle within μ steps (the tail length), and from then on the gap closes by one node per step, so they meet within λ more steps (the cycle length).

*JS note:* `slow === fast` compares **node identity**. Comparing `.val` instead would falsely report a cycle for `1→1→1→1` (this case is in the tests).

*See also:* Floyd's cycle detection under **Linked Lists** below; the same technique also finds the middle node.

*Follow-up:*
- **"Where does the cycle start?"** See Q15.
- **"How long is the cycle?"** After the pointers meet, walk one of them around the loop until it gets back, counting steps.
- **Baseline first:** a `Set` of visited nodes is the O(n)-space answer to mention before Floyd.
- **Implicit linked lists** use the same trick. In **Happy Number**, each number points to the next. In **Find the Duplicate Number** (LC 287), `i → nums[i]` forms a list, and the cycle's entry is the duplicate.

**Q15. Detect Cycle in Linked List** *(Amazon, Google, Microsoft)* — `1→2→3→4→5→(back to 3)` → cycle exists (entry node `3`)

The source asks the same question as Q12 and gives the same C++ (only the comments differ). So instead of a copy, the JS here extends Floyd to the follow-up interviewers ask next: **return the node where the cycle begins** (Linked List Cycle II). `hasCycle(head)` is then just `detectCycle(head) !== null`.

- **Phase 1** (same as Q12): slow moves 1 step and fast moves 2. If they meet, there's a cycle.
- **Phase 2:** restart one pointer at `head`, then advance both one step at a time. They meet at the cycle's entry.
- **Why phase 2 works:** let μ be the tail length and λ the cycle length. At the first meeting, slow has walked μ + a steps and fast has walked 2(μ + a), so μ + a is a multiple of λ. From the meeting point, μ more steps land exactly on the entry, and μ steps from `head` land there too.

```js
function detectCycle(head) {
  let slow = head, fast = head;
  while (fast && fast.next) {               // Phase 1 — identical to Q12
    slow = slow.next;
    fast = fast.next.next;
    if (slow === fast) {
      let p = head;                         // Phase 2 — one pointer restarts at head,
      while (p !== slow) {                  // both move 1 step; they meet at the cycle entry
        p = p.next;
        slow = slow.next;
      }
      return p;                             // entry node (hasCycle ⇔ detectCycle(head) !== null)
    }
  }
  return null;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(NULL) {}
};

bool hasCycle(ListNode* head) {
    if (!head || !head->next) return false;
    ListNode* slow = head;
    ListNode* fast = head;

    while (fast && fast->next) {
        slow = slow->next;          // 1 step
        fast = fast->next->next;    // 2 steps
        if (slow == fast) return true;  // Meet
    }

    return false;  // fast reached NULL
}
```

</details>

**Complexity:** O(N) time (both phases are linear), O(1) space.

```text
1→2→3→4→5→(3)     μ = 2 (nodes 1,2), λ = 3 (nodes 3,4,5)
Phase 1: step 1 slow=2 fast=3 | step 2 slow=3 fast=5 | step 3 slow=4 fast=4 → meet at 4
Phase 2: p=1, slow=4 → p=2, slow=5 → p=3, slow=3 → entry = node 3
No cycle 1→2→3→4→null: slow=2 fast=3 | slow=3 fast=null → null
```

💡 *FAANG tip:* Floyd's cycle detection is asked very frequently in interviews. It's also used in real-world scenarios like loop detection in systems and routing problems.

*Source note:* this duplicates Q12. The source's own Q15 dry run (the pointers meet at node 4 for `1→…→5→3`) is correct. Its complexity box repeats the "each node visited at most once" claim, which is inaccurate for the reason explained under Q12. The JS was also checked against a `Set`-based oracle on 300 randomly generated lists, with and without cycles.

*Follow-up:*
- **"Prove phase 2":** the μ + a argument above is what they're looking for.
- **"What if you can modify the list?"** You can mark visited nodes instead, but that's destructive, so say so.
- Everything else is as for Q12.

**Q13. Merge Two Sorted Lists** *(Amazon, Google, Microsoft)* — `1→2→4` + `1→3→4` → `1→1→2→3→4→4`

Merge two sorted linked lists into one sorted list and return its head.

- Start from a dummy node, so you never have to special-case which list the first node comes from.
- Repeatedly attach the smaller of the two current nodes, then advance that list.
- When one list runs out, attach the rest of the other in a single step.

```js
function mergeTwoLists(list1, list2) {
  const dummy = new ListNode(0);            // sentinel: no "is this the first node?" special case
  let tail = dummy;
  while (list1 && list2) {
    if (list1.val <= list2.val) {           // <= keeps the merge stable (list1 wins ties)
      tail.next = list1;
      list1 = list1.next;
    } else {
      tail.next = list2;
      list2 = list2.next;
    }
    tail = tail.next;
  }
  tail.next = list1 ? list1 : list2;        // splice the leftover run in one step
  return dummy.next;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(NULL) {}
};

ListNode* mergeTwoLists(ListNode* list1, ListNode* list2) {
    ListNode dummy(0);
    ListNode* tail = &dummy;

    while (list1 && list2) {
        if (list1->val <= list2->val) {
            tail->next = list1;
            list1 = list1->next;
        } else {
            tail->next = list2;
            list2 = list2->next;
        }
        tail = tail->next;
    }

    tail->next = (list1) ? list1 : list2;
    return dummy.next;
}
```

</details>

**Complexity:** O(m + n) time (each node is attached once), O(1) space (the existing nodes are relinked, not copied).

```text
list1: 1→2→4   list2: 1→3→4
take 1 (list1, ties go to list1) → dummy→1
take 1 (list2)                   → 1→1
take 2 (list1)                   → 1→1→2        list1 now at 4
take 3 (list2)                   → 1→1→2→3      list2 now at 4
take 4 (list1)                   → …→3→4        list1 now null
attach the rest of list2 (4)     → 1→1→2→3→4→4
```

💡 *FAANG tip:* A dummy node greatly simplifies edge cases, such as a merged list that could start with a node from either list.

*Source note:* rows 3–4 of the dry run lag one step behind. After `2` is taken, `list1` should already point to `4`, and after `3` is taken, `list2` should point to `4`. The merged column and the final answer are correct.

*See also:* the dummy-head bullet under **Linked Lists** below.

*Follow-up:*
- **"Recursive version?"** It's shorter, but it uses O(m + n) stack.
- **Merge k sorted lists:** see Q18.
- **Sort List** (LC 148): merge sort on a linked list. Find the middle with fast/slow pointers, sort each half, then merge the halves with this function.

**Q14. Remove Nth Node From End** *(Amazon, Google, Microsoft)* — `1→2→3→4→5, n = 2` → `1→2→3→5`

Remove the n-th node from the end of the list and return its head.

- Put a dummy node in front of `head`, and start both `fast` and `slow` on it.
- Move `fast` n steps ahead.
- Move both pointers together until `fast` is on the last node. `slow` is now just *before* the node to delete.
- Unlink `slow.next`. The dummy covers the case where the head itself is removed.

```js
function removeNthFromEnd(head, n) {
  const dummy = new ListNode(0, head);
  let fast = dummy;
  let slow = dummy;
  for (let i = 0; i < n; i++) fast = fast.next;   // Step 1: open an n-node gap
  while (fast.next) {                             // Step 2: slide until fast is on the last node
    fast = fast.next;
    slow = slow.next;
  }
  slow.next = slow.next.next;                     // Step 3: unlink (no `delete` — GC reclaims it)
  return dummy.next;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
ListNode* removeNthFromEnd(ListNode* head, int n) {
    ListNode dummy(0);
    dummy.next = head;
    ListNode* fast = &dummy;
    ListNode* slow = &dummy;

    // Step 1: Move fast n steps ahead
    for (int i = 0; i < n; i++)
        fast = fast->next;

    // Step 2: Move both until fast reaches end
    while (fast->next) {
        fast = fast->next;
        slow = slow->next;
    }

    // Step 3: Delete the nth node from end
    ListNode* toDelete = slow->next;
    slow->next = slow->next->next;
    delete toDelete;

    return dummy.next;
}
```

</details>

**Complexity:** O(L) time in a single pass, O(1) space.

```text
d→1→2→3→4→5, n = 2
fast moves 2:  fast=2 slow=d
slide:         fast=3 slow=1 | fast=4 slow=2 | fast=5 slow=3   (fast.next = null → stop)
slow=3, slow.next=4 → unlink node 4
→ 1→2→3→5
```

💡 *FAANG tip:* Always use a dummy node to handle the case where the head itself is the node to be removed.

*Source note:* **the source's dry run removes the wrong node.** It says "slow→next = 5 (to delete)" and gives the result `1→2→3→4`. For n = 2, the 2nd node from the end is **4**, so the correct result is `1→2→3→5`. The C++ itself is correct: the source's own trace ends with `slow` on node 3, and `slow->next` is node 4 (verified in Node). The visualisation repeats the mistake ("Delete slow→next (node 5)").

Two smaller points:
- The claim "we traverse the list at most twice" is misleading. This is a single pass with two pointers; it's the *two-pass* version that counts the length first.
- In C++, `delete toDelete` assumes the nodes were allocated with `new`. In JS you just unlink the node and the GC reclaims it.

*See also:* the fixed gap between the pointers is the same idea as a fixed-size sliding window, under **Arrays, Strings, Hashing…** above.

*Follow-up:*
- **"What if `n` is larger than the length?"** The first loop steps past the end, and in JS `fast.next` on `null` throws a `TypeError`, so validate `n` first.
- **"Two-pass version?"** Count the length L, then remove the node at index L − n. Mention it first, then give the one-pass version.
- **Swapping Nodes in a Linked List** (swap the k-th node from the start with the k-th from the end) uses the same gap trick.

**Q16. Intersection of Two Linked Lists** *(Amazon, Google, Microsoft)* — A: `1→2→3→8→9`, B: `4→5→6→7→8→9` (sharing `8→9`) → node `8`

Return the node where two singly linked lists intersect, or `null` if they don't.

- Walk pointer `pA` along A and `pB` along B.
- When a pointer reaches the end, redirect it to the head of the *other* list.
- Both pointers then travel the same total distance (`lenA + lenB`), so they reach the intersection node together. With no intersection, they reach `null` together and the loop ends.

```js
function getIntersectionNode(headA, headB) {
  if (!headA || !headB) return null;
  let pA = headA;
  let pB = headB;
  while (pA !== pB) {                             // node identity, not .val
    pA = pA === null ? headB : pA.next;           // end of A → continue on B
    pB = pB === null ? headA : pB.next;           // end of B → continue on A
  }
  return pA;                                      // intersection node, or null if none
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
ListNode* getIntersectionNode(ListNode* headA, ListNode* headB) {
    if (!headA || !headB) return NULL;

    ListNode* pA = headA;
    ListNode* pB = headB;

    while (pA != pB) {
        pA = (pA == NULL) ? headB : pA->next;
        pB = (pB == NULL) ? headA : pB->next;
    }

    return pA;  // Intersection node or NULL
}
```

</details>

**Complexity:** O(m + n) time (each pointer walks both lists at most once), O(1) space.

```text
A: 1→2→3→8→9   B: 4→5→6→7→8→9   (8 and 9 are the SAME nodes)
move  pA     pB
0     1      4
1     2      5
2     3      6
3     8      7
4     9      8
5     null   9
6     4 (B)  null
7     5      1 (A)
8     6      2
9     7      3
10    8      8   → same node → return 8
```

💡 *FAANG tip:* This is a classic two-pointer question. The key insight is to make both pointers travel the same total distance.

*Source note:* the intersection is **by node identity**. The diagram draws 8→9 twice, but they're the same node objects. Two lists that merely contain equal values don't intersect (this case is in the tests). The visualisation's step numbers are also off by one: at "step 5" `pB` is on node 9, not 4, and the pointers meet at move 10, not step 9.

*See also:* the intersection bullet under **Linked Lists** below.

*Follow-up:*
- **"Simpler versions first?"** Put A's nodes in a hash set, then walk B: O(m + n) time, O(m) space. Or use the length-difference approach: advance the longer list by `|m − n|`, then walk both together.
- **"What if the lists can contain cycles?"** Detect each cycle first (Q15), then compare the entry nodes.
- **LCA with parent pointers:** this is exactly this problem, walking upwards from `p` and `q` (compare Q26).

**Q17. Add Two Numbers (Linked List)** *(Amazon, Google, Microsoft)* — `2→4→3` (342) + `5→6→4` (465) → `7→0→8` (807)

Two non-empty lists store non-negative integers, one digit per node, in **reverse** order. Return their sum as a list in the same format.

- Walk both lists together, building the result from a dummy head.
- At each position, compute `sum = carry + digitA + digitB`. Emit `sum % 10` and carry `floor(sum / 10)`.
- Keep looping while *either* list has digits left *or* a carry remains, so a final carry becomes its own node.

```js
function addTwoNumbers(l1, l2) {
  const dummy = new ListNode(0);
  let curr = dummy;
  let carry = 0;
  while (l1 || l2 || carry) {
    let sum = carry;
    if (l1) { sum += l1.val; l1 = l1.next; }
    if (l2) { sum += l2.val; l2 = l2.next; }
    carry = Math.floor(sum / 10);                 // C++ int division truncates; JS `/` gives 1.5
    curr.next = new ListNode(sum % 10);
    curr = curr.next;
  }
  return dummy.next;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(NULL) {}
};

ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
    ListNode* dummy(0);
    ListNode* curr = &dummy;
    int carry = 0;

    while (l1 || l2 || carry) {
        int sum = carry;
        if (l1) { sum += l1->val; l1 = l1->next; }
        if (l2) { sum += l2->val; l2 = l2->next; }

        carry = sum / 10;
        curr->next = new ListNode(sum % 10);
        curr = curr->next;
    }
    return dummy.next;
}
```

</details>

**Complexity:** O(max(m, n)) time. O(1) *auxiliary* space; the result list itself is O(max(m, n)).

```text
342 + 465
step  a  b  carry-in  sum  digit  carry-out
0     2  5  0         7    7      0
1     4  6  0         10   0      1
2     3  4  1         8    8      0
→ 7→0→8
```

💡 *FAANG tip:* Don't forget the remaining carry once both lists are exhausted. A dummy node also avoids edge cases while the result list is still empty.

*Source note:* **the source's C++ doesn't compile.** `ListNode* dummy(0);` declares a *null pointer*, not a node. That makes `&dummy` a `ListNode**`, which can't initialise `ListNode* curr`, and `dummy.next` is invalid on a pointer. It should be `ListNode dummy(0);`, as in the source's own Q13 and Q14. Also, the "O(1) space" claim only holds if you exclude the output list.

*JS note:* C++ `sum / 10` on `int`s truncates, but JS `/` returns `1.5` for `15 / 10`, so a literal translation produces fractional carries. Use `Math.floor(sum / 10)` or `(sum / 10) | 0`.

*See also:* the carry-propagation bullet under **Linked Lists** below.

*Follow-up:*
- **"What if the digits are stored in *forward* order?"** (Add Two Numbers II.) Reverse both lists first, or push the digits onto two stacks and build the result by prepending.
- **"Why not convert to numbers and add?"** The lists can be arbitrarily long. The values overflow `int`/`long` in C++ and lose precision past 2⁵³ in JS. `BigInt` would work, but it misses the point of the question.
- **Multiply Strings** and **Add Binary** use the same digit-by-digit carry loop.

### Heaps & Data-Structure Design

**Q18. Merge K Sorted Lists** *(Amazon, Google, Microsoft)* — `[1→4→5, 1→3→4, 2→6]` → `1→1→2→3→4→4→5→6`

Merge k sorted linked lists into one sorted list.

- Push the head of every non-empty list into a min-heap keyed by `val`.
- Repeatedly pop the smallest node, append it to the result, and push that node's `next` (if there is one).
- The heap never holds more than k nodes, one "front" per list.

```js
class MinHeap {                                   // JS has no built-in priority queue
  constructor(compare) {
    this.a = [];
    this.cmp = compare;                           // < 0 means "first argument comes out first"
  }
  size() { return this.a.length; }
  push(x) {
    const a = this.a;
    a.push(x);
    let i = a.length - 1;
    while (i > 0) {                               // sift up
      const p = (i - 1) >> 1;
      if (this.cmp(a[i], a[p]) >= 0) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }
  pop() {
    const a = this.a;
    const top = a[0];
    const last = a.pop();
    if (a.length > 0) {
      a[0] = last;
      let i = 0;
      for (;;) {                                  // sift down
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]];
        i = m;
      }
    }
    return top;
  }
}

function mergeKLists(lists) {
  const minHeap = new MinHeap((a, b) => a.val - b.val);  // C++ CompareNode (a->val > b->val) = min-heap
  for (const node of lists) if (node) minHeap.push(node);
  const dummy = new ListNode(0);
  let curr = dummy;
  while (minHeap.size() > 0) {
    const node = minHeap.pop();                   // smallest head among the k lists
    curr.next = node;
    curr = curr.next;
    if (node.next) minHeap.push(node.next);       // its successor takes its place
  }
  return dummy.next;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
struct CompareNode {
    bool operator()(ListNode* a, ListNode* b) {
        return a->val > b->val;   // min-heap
    }
};

ListNode* mergeKLists(vector<ListNode*>& lists) {
    priority_queue<ListNode*, vector<ListNode*>, CompareNode> minHeap;

    for (auto node : lists) {
        if (node) minHeap.push(node);
    }

    ListNode dummy(0);
    ListNode* curr = &dummy;

    while (!minHeap.empty()) {
        ListNode* node = minHeap.top();
        minHeap.pop();

        curr->next = node;
        curr = curr->next;

        if (node->next) {
            minHeap.push(node->next);
        }
    }
    return dummy.next;
}
```

</details>

**Complexity:** O(N log k) time, where N = total nodes and k = number of lists: each node is pushed and popped once, at O(log k) each. O(k) space for the heap.

```text
L1: 1→4→5   L2: 1→3→4   L3: 2→6
heap (top first)          pop     result
[1(L1) 1(L2) 2(L3)]       1(L1)   1
[1(L2) 2(L3) 4(L1)]       1(L2)   1→1
[2(L3) 3(L2) 4(L1)]       2(L3)   …→2
[3(L2) 4(L1) 6(L3)]       3(L2)   …→3
[4(L1) 4(L2) 6(L3)]       4(L1)   …→4
[4(L2) 5(L1) 6(L3)]       4(L2)   …→4
[5(L1) 6(L3)]             5(L1)   …→5
[6(L3)]                   6(L3)   …→6
```

💡 *FAANG tip:* A min-heap is the most optimal approach. The brute force, repeatedly scanning all k heads for the smallest node, takes O(N·k), which isn't acceptable for large inputs.

*Source note:* the heap is optimal, but it isn't the *only* optimal approach. Divide and conquer also reaches O(N log k): merge the lists in pairs with Q13's `mergeTwoLists`, halving k each round. It needs no heap and only O(1) extra space when done iteratively. It's often the better live answer in JavaScript, because there's no built-in heap to lean on.

The C++ comparator reads backwards on purpose. `std::priority_queue` is a max-heap, so `a->val > b->val` (meaning "a has lower priority") turns it into a min-heap. A JS comparator follows the `sort()` convention instead: a negative result means `a` comes out first.

*JS note:* JS has no `PriorityQueue`, so either write the ~35-line binary heap above (worth memorising; it was checked against sorting 500 random numbers) or ask the interviewer whether you can assume one. Sorting all the values and rebuilding the list is O(N log N). That's a valid baseline to mention, as long as you use `(a, b) => a - b`.

*See also:* heaps under **Sorting, Searching, Heaps & Randomized Structures** below.

*Follow-up:*
- **Divide and conquer:** see the source note above.
- **Merge k sorted arrays** and **external merge sort** (merging sorted chunks that don't fit in memory) use the same heap.
- **Smallest Range Covering Elements from K Lists** (LC 632) runs the same heap while also tracking the current maximum.
- **Kth Smallest Element in a Sorted Matrix** treats each row as a sorted list.

**Q19. LRU Cache** *(Amazon, Google, Microsoft)* — capacity 2: `put(1,1) put(2,2) get(1) put(3,3) get(2) put(4,4) get(1) get(3) get(4)` → `1, -1, -1, 3, 4`

Design a Least Recently Used (LRU) cache with two operations, both O(1):
- `get(key)`: return the value, or −1 if the key isn't cached.
- `put(key, value)`: insert or update the key. When the cache is full, evict the least recently used key first.

The approach:
- A **doubly linked list** keeps usage order. The most recent entry sits right after the `head` dummy node, and the least recent sits just before the `tail` dummy.
- A **hash map** of `key → node` reaches any node in O(1), so it can be unlinked in O(1). That's why the list must be *doubly* linked.
- `get` and `put` move the touched node to the front. When full, evict `tail.prev` and delete its key from the map. That's why each node stores its own key.

```js
class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.mp = new Map();                                  // key → node
    this.head = { key: 0, value: 0, prev: null, next: null };  // dummy, MRU side
    this.tail = { key: 0, value: 0, prev: null, next: null };  // dummy, LRU side
    this.head.next = this.tail;
    this.tail.prev = this.head;
  }
  addFront(node) {                                        // insert right after head
    node.next = this.head.next;
    node.prev = this.head;
    this.head.next.prev = node;
    this.head.next = node;
  }
  removeNode(node) {                                      // O(1) unlink
    node.prev.next = node.next;
    node.next.prev = node.prev;
  }
  get(key) {
    if (!this.mp.has(key)) return -1;
    const node = this.mp.get(key);
    this.removeNode(node);                                // touch → move to front
    this.addFront(node);
    return node.value;
  }
  put(key, value) {
    if (this.capacity <= 0) return;                       // guard: C++ original would evict the dummy head
    if (this.mp.has(key)) {                               // update existing
      const node = this.mp.get(key);
      node.value = value;
      this.removeNode(node);
      this.addFront(node);
    } else {                                              // new key
      if (this.mp.size === this.capacity) {               // full → evict LRU (node before tail)
        const lru = this.tail.prev;
        this.removeNode(lru);
        this.mp.delete(lru.key);                          // why each node stores its own key
      }
      const node = { key, value, prev: null, next: null };
      this.addFront(node);
      this.mp.set(key, node);
    }
  }
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
class LRUCache {
private:
    struct Node {
        int key, value;
        Node *prev, *next;
        Node(int k, int v) : key(k), value(v), prev(nullptr), next(nullptr) {}
    };

    int capacity;
    unordered_map<int, Node*> mp;
    Node *head, *tail;  // dummy nodes

    void addFront(Node* node) {
        node->next = head->next;
        node->prev = head;
        head->next->prev = node;
        head->next = node;
    }

    void removeNode(Node* node) {
        node->prev->next = node->next;
        node->next->prev = node->prev;
    }

public:
    LRUCache(int cap) {
        capacity = cap;
        head = new Node(0,0);
        tail = new Node(0,0);
        head->next = tail;
        tail->prev = head;
    }

    int get(int key) {
        if (mp.find(key) == mp.end()) return -1;
        Node* node = mp[key];
        removeNode(node);
        addFront(node);
        return node->value;
    }   // [brace restored — lost at the column break in the source image]

    void put(int key, int value) {
        if (mp.find(key) != mp.end()) {
            // Update existing
            Node* node = mp[key];
            node->value = value;
            removeNode(node);
            addFront(node);
        } else {
            // New key
            if ((int)mp.size() == capacity) {
                // Remove LRU
                Node* lru = tail->prev;
                removeNode(lru);
                mp.erase(lru->key);
                delete lru;
            }
            Node* node = new Node(key, value);
            addFront(node);
            mp[key] = node;
        }
    }
};
```

</details>

**Complexity:** O(1) time for both `get()` and `put()`, O(capacity) space.

```text
op        list (MRU → LRU)   returns
put(1,1)  [1]
put(2,2)  [2, 1]
get(1)    [1, 2]             1
put(3,3)  [3, 1]             (evicts 2)
get(2)    [3, 1]             -1
put(4,4)  [4, 3]             (evicts 1)
get(1)    [4, 3]             -1
get(3)    [3, 4]             3
get(4)    [4, 3]             4
```

💡 *FAANG tip:* A must-do question for system design rounds. Know how to implement a doubly linked list and combine it with a hash map for O(1) operations.

*Source note:*
- **Missing brace:** in the image, the closing brace of `get()` is lost at the column break. It's restored and marked in the C++ above.
- **Unreadable constructor:** the `Node` constructor's initialiser list is too small to read, so it has been reconstructed as `prev(nullptr), next(nullptr)`.
- **Memory leak:** the C++ has no destructor, so the dummy nodes and any remaining entries leak. JS's garbage collector makes that moot.
- **Capacity 0:** `put` would "evict" `tail->prev`, which is the dummy `head`, and crash on its null `prev`. LeetCode guarantees capacity ≥ 1, but the JS version guards against it (tested).

*See also:* the LRU bullets under **Sorting, Searching, Heaps…** and **Intervals, Caching…** below, which explain the `Map` insertion-order trick in prose.

*Follow-up:* "In JavaScript, can you do it with less code?" Yes. A `Map` iterates in insertion order, so deleting a key and re-inserting it moves it to the "most recent" end, and `map.keys().next().value` is always the least recent key. Both operations stay O(1) with no hand-written list. This version passes the same tests as the one above:

```js
class LRUCacheMap {
  constructor(capacity) {
    this.capacity = capacity;
    this.map = new Map();                   // iteration order = insertion order = recency order
  }
  get(key) {
    if (!this.map.has(key)) return -1;
    const value = this.map.get(key);
    this.map.delete(key);                   // re-insert → becomes most recent
    this.map.set(key, value);
    return value;
  }
  put(key, value) {
    this.map.delete(key);
    this.map.set(key, value);
    if (this.map.size > this.capacity) {
      this.map.delete(this.map.keys().next().value);   // first key = least recently used
    }
  }
}
```

Say out loud that this relies on a spec guarantee (`Map` insertion order) rather than an explicit data structure, and offer the linked-list version if they want the "real" one. From there, the usual escalations are:
- **LFU Cache:** frequency buckets, each holding its own LRU list.
- **TTL expiry:** entries that expire after a set time.
- **Concurrency:** "make it safe under concurrent access".

### Graphs (BFS)

**Q20. Word Ladder (Length)** *(Amazon, Google, Microsoft)* — `beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]` → `5` (`hit → hot → dot → dog → cog`)

Return the number of words in the shortest transformation sequence from `beginWord` to `endWord`, or 0 if no such sequence exists. Each step changes exactly one letter, and every intermediate word must be in `wordList`.

- Treat each word as a graph node, with an edge between words that differ by one letter. The graph is unweighted, so **BFS** finds the shortest path.
- Process the queue level by level, where each level is one transformation. Return the level number the first time `endWord` is dequeued.
- To find neighbours, try all 26 letters at every position, keeping candidates that are in the word set and not yet visited.
- Mark a word visited when you **enqueue** it, not when you dequeue it, so it's never queued twice.

```js
function ladderLength(beginWord, endWord, wordList) {
  const words = new Set(wordList);
  if (!words.has(endWord)) return 0;
  const q = [beginWord];
  let head = 0;                                   // queue via index pointer (Array.shift() is O(n))
  const visited = new Set([beginWord]);
  let level = 1;
  while (head < q.length) {
    let size = q.length - head;                   // words on the current level
    while (size-- > 0) {
      const word = q[head++];
      if (word === endWord) return level;
      const chars = word.split('');               // JS strings are immutable → mutate a char array
      for (let i = 0; i < chars.length; i++) {
        const original = chars[i];
        for (let c = 97; c <= 122; c++) {         // 'a'..'z'
          const ch = String.fromCharCode(c);
          if (ch === original) continue;
          chars[i] = ch;
          const next = chars.join('');
          if (words.has(next) && !visited.has(next)) {
            q.push(next);
            visited.add(next);                    // mark on PUSH, not on pop
          }
        }
        chars[i] = original;
      }
    }
    level++;
  }
  return 0;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
int ladderLength(string beginWord, string endWord, vector<string>& wordList) {
    unordered_set<string> words(wordList.begin(), wordList.end());
    if (words.find(endWord) == words.end()) return 0;

    queue<string> q;
    q.push(beginWord);
    unordered_set<string> visited;
    visited.insrert(beginWord);
    int level = 1;

    while (!q.empty()) {
        int size = q.size();
        while (size--) {
            string word = q.front(); q.pop();
            if (word == endWord) return level;

            for (int i = 0; i < word.size(); i++) {
                char original = word[i];
                for (char c = 'a'; c <= 'z'; c++) {
                    if (c == original) continue;
                    word[i] = c;
                    if (words.count(word) && !visited.count(word)) {
                        q.pusk(word);
                        visited.insert(word);
                    }
                }
                word[i] = original;
            }
        }
        level++;
    }   // [brace restored — missing in the source image]
    return 0;
}
```

</details>

**Complexity:** O(N·M²) time for N words of length M (see the source note), and O(N·M) space for the word set, the visited set and the queue.

```text
level 1: hit
level 2: hot                 (h_t → hot)
level 3: dot, lot
level 4: dog, log
level 5: cog  → dequeued == endWord → return 5
neighbours of "hot": aot…zot, hat…hzt, hoa…hoz = 3 × 25 candidates
```

💡 *FAANG tip:* BFS guarantees the shortest path in an unweighted graph. Mark a word visited as soon as you push it into the queue (not when you pop it) to avoid duplicates.

*Source note:*
1. **The source's C++ doesn't compile.** `visited.insrert(...)` and `q.pusk(...)` are typos, and the brace that closes the outer `while` is missing from the image. The typos are kept as printed above; the brace is restored and marked.
2. **The time complexity is understated.** For each of the N words, the code tries M × 26 candidates, and building and hashing each candidate string costs O(M). That makes it O(N·M²·26), i.e. O(N·M²), not O(N·M·26). This matches the standard analysis.
3. **Neighbour count:** the example says "3 · 26 (except same letter)". Excluding the same letter, that's 3 × 25 = 75 candidates.

*JS note:* JS strings are immutable, so `word[i] = c` silently does nothing. The JS version mutates a `chars` array instead and joins it back into a string. Also, `q.shift()` is O(n) per call, so a BFS over a large dictionary should use a read index (`head`) as above, or swap in a fresh array per level.

*See also:* the BFS-for-shortest-path bullet under **Graphs — BFS/DFS, Topological Sort & Union-Find** below.

*Follow-up:*
- **Word Ladder II:** return *all* shortest sequences. Run BFS while recording each word's parents, then backtrack from `endWord` with DFS.
- **Bidirectional BFS:** expand the smaller frontier from both ends. It cuts the explored space dramatically, and it's the common answer to "how would you speed this up?".
- **Wildcard buckets:** precompute buckets like `h*t → [hot, hit, …]` so neighbours come from a lookup instead of 26-letter probing.
- **Minimum Genetic Mutation:** the same problem with the alphabet `ACGT`.

### Trees & BSTs

The tree answers share this node class. The source doesn't print its `TreeNode`, so this follows LeetCode's shape:

```js
class TreeNode {
  constructor(val = 0, left = null, right = null) {
    this.val = val;
    this.left = left;
    this.right = right;
  }
}
```

**Q25. Binary Tree Level Order Traversal** *(Amazon, Google, Microsoft)* — `[3,9,20,null,null,15,7]` → `[[3],[9,20],[15,7]]`

Return the tree's node values level by level, left to right.

- Run BFS with a queue, starting from the root.
- Snapshot `levelSize`, the current queue length. Process exactly that many nodes (one full level), collecting their values and enqueueing their children.
- Push each level's array into the result.

```js
function levelOrder(root) {
  const result = [];
  if (!root) return result;
  let queue = [root];
  while (queue.length > 0) {
    const levelSize = queue.length;               // snapshot = number of nodes on this level
    const level = [];
    const next = [];
    for (let i = 0; i < levelSize; i++) {
      const node = queue[i];
      level.push(node.val);
      if (node.left) next.push(node.left);
      if (node.right) next.push(node.right);
    }
    result.push(level);
    queue = next;                                 // swap in the next level (no O(n) shift())
  }
  return result;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
vector<vector<int>> levelOrder(TreeNode* root) {
    vector<vector<int>> result;
    if (!root) return result;
    queue<TreeNode*> q;
    q.push(root);

    while (!q.empty()) {
        int levelSize = q.size();
        vector<int> level;

        // process current level
        for (int i = 0; i < levelSize; i++) {
            TreeNode* node = q.front(); q.pop();
            level.push_back(node->val);
            if (node->left)  q.push(node->left);
            if (node->right) q.push(node->right);
        }
        result.push_back(level);
    }
    return result;
}
```

</details>

**Complexity:** O(n) time (each node visited exactly once). O(w) space for the queue, where w is the maximum width of the tree, up to about n/2 for a complete tree. The output itself is O(n).

```text
    3
   / \
  9  20
     / \
    15  7
queue [3]      → level [3]      next [9,20]
queue [9,20]   → level [9,20]   next [15,7]
queue [15,7]   → level [15,7]   next []
→ [[3], [9,20], [15,7]]
```

💡 *FAANG tip:* Level-order traversal is a classic BFS pattern. Make sure you process every node on the current level before moving on to the next.

*JS note:* the C++ `q.pop()` is O(1), but the usual JS equivalent, `queue.shift()`, is O(n) per call, so on a big tree BFS turns quadratic. The JS version keeps the source's `levelSize` idea but reads the current level by index and swaps in a fresh `next` array. That also keeps memory at O(w), unlike a read-pointer queue that holds on to every visited node.

*See also:* the BFS bullet under **Trees, BSTs & Tries** below (right-side view, zigzag, multi-source spread).

*Follow-up:* the same template covers most variants:
- **Zigzag order:** reverse every other `level`.
- **Right side view:** keep the last value of each level.
- **Level averages / largest value per level:** reduce each `level`.
- **Bottom-up order:** `result.reverse()`.
- **Minimum depth:** return at the first leaf you reach.

"DFS instead?" Pass `depth` down the recursion and push into `result[depth]`. That uses an O(h) stack instead of an O(w) queue.

**Q26. Lowest Common Ancestor of a Binary Tree** *(Amazon, Google, Microsoft)* — tree `[3,5,1,6,2,0,8,null,null,7,4]`, `p = 5, q = 1` → `3`

Find the lowest node that has both `p` and `q` as descendants. A node counts as its own descendant.

- If `root` is `null`, `p` or `q`, return it. This reports "found something here" upwards.
- Recurse into both subtrees.
- If *both* sides return non-null, `p` and `q` are on different sides, so this node is the LCA. Otherwise, pass up whichever side found something.
- If `p` is an ancestor of `q`, the recursion stops at `p` and returns it, which is the correct answer.

```js
function lowestCommonAncestor(root, p, q) {
  if (!root || root === p || root === q) return root;   // hit p/q (or fell off) → report it upward
  const left = lowestCommonAncestor(root.left, p, q);
  const right = lowestCommonAncestor(root.right, p, q);
  if (left && right) return root;                // p and q on different sides → this is the fork
  return left ? left : right;                    // otherwise pass up whichever side found something
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
TreeNode* lowestCommonAncestor(TreeNode* root,
                               TreeNode* p, TreeNode* q) {
    if (!root || root == p || root == q)
        return root;

    TreeNode* left = lowestCommonAnecstor(root->left, p, q);
    TreeNode* right = lowestCommonAncestor(root->right, p, q);

    if (left && right) return root;   // p and q in different sides
    return left ? left : right;       // return non-NULL side
}
```

</details>

**Complexity:** O(n) time (each node visited at most once), O(h) space for the recursion stack.

```text
          3
        /   \
       5     1
      / \   / \
     6   2 0   8
        / \
       7   4
lca(3): lca(5) → 5 is p → return 5 immediately (6, 2, 7, 4 never visited)
        lca(1) → 1 is q → return 1 immediately (0, 8 never visited)
        left=5, right=1 → both non-null → LCA = 3
```

💡 *FAANG tip:* This is a classic post-order DFS pattern. The key idea: if both left and right return non-null, the current node is the LCA. Handle the case where one node is an ancestor of the other.

*Source note:*
1. **A typo stops it compiling:** the left recursive call is spelled `lowestCommonAnecstor`.
2. **The dry run is misleading.** It shows a full post-order walk that visits 6, 7, 4 and 2 *before* 5. But the `root == p || root == q` check runs *before* the recursion, so the call on node 5 returns immediately without visiting its subtree, and the same happens at node 1. Only nodes 3, 5 and 1 are ever visited (verified). That early return is also what makes the ancestor case work.
3. **Both nodes are assumed to exist.** If only one of `p` and `q` is in the tree, the code returns that node, which is the wrong answer for **LCA II** (LC 1644).

*See also:* the LCA bullet under **Trees, BSTs & Tries** below, including the O(h) BST variant.

*Follow-up:*
- **LCA in a BST:** walk down from the root, going left if both values are smaller and right if both are larger. The first node where they split is the answer. This is O(h), iterative, with no recursion.
- **p or q may not exist:** count how many you actually found before trusting the answer.
- **Nodes have parent pointers:** this becomes Q16 (intersection of two lists), walking upwards.
- **LCA of many nodes:** generalise the base case to "root is in the set".

**Q27. Validate Binary Search Tree** *(Amazon, Google, Microsoft)* — `[5,3,8,1,4,7,9]` → `true`

Determine whether a binary tree is a valid BST. Every node in a left subtree must be `<` the node, every node in a right subtree must be `>` the node, and both subtrees must be BSTs themselves.

- An in-order traversal of a valid BST produces a **strictly increasing** sequence.
- Traverse in order, remembering the previous value. If the current value is `<=` the previous one, it isn't a BST.
- The `first` flag means "no previous value yet". It avoids picking a sentinel like `-Infinity` or `INT_MIN`, which could collide with a real node value.

```js
function isValidBST(root) {
  let prev = 0;
  let first = true;                              // "no previous value yet" (C++ member flag)
  function inorder(node) {
    if (!node) return true;
    if (!inorder(node.left)) return false;
    if (!first && node.val <= prev) return false;   // inorder must be STRICTLY increasing
    first = false;
    prev = node.val;
    return inorder(node.right);
  }
  return inorder(root);
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
class Solution {
private:
    long long prev;   // use long long to handle INT_MIN
    bool first;       // to handle first node

    bool inorder(TreeNode* root) {
        if (!root) return true;

        if (!inorder(root->left)) return false;

        if (!first && root->val <= prev) return false;
        first = false;
        prev = root->val;

        return inorder(root->right);
    }

public:
    bool isValidBST(TreeNode* root) {
        prev = 0;
        first = true;
        return inorder(root);
    }
};
```

</details>

**Complexity:** O(n) time, and it can stop early at the first violation. O(h) space for the recursion stack.

```text
        5
      /   \
     3     8
    / \   / \
   1   4 7   9
in-order: 1 → 3 → 4 → 5 → 7 → 8 → 9   strictly increasing ✓ → true
[5,1,4,null,null,3,6]: in-order 1, 5, 3 → 3 <= 5 ✗ → false
```

💡 *FAANG tip:* In-order traversal removes the need to pass a min/max range down the recursion, which makes the code cleaner and less error-prone.

*Source note:* the comment "use long long to handle INT_MIN" is redundant. The `first` flag already handles a node whose value is `INT_MIN`. A 64-bit `prev` would only matter for the *sentinel* approach (`prev = LLONG_MIN`). The code itself is correct (tested with `INT_MIN` nodes). The classic bug this approach avoids is checking each node only against its immediate children. That misses violations like `[5,4,6,null,null,3,7]`, where 3 sits in 5's right subtree (this case is in the tests).

*JS note:* JS numbers are doubles, so there's no overflow question. Starting from `prev = -Infinity` would also be safe *unless* a node can hold `-Infinity`, so the flag is the more robust choice.

*See also:* the validate-BST bullet under **Trees, BSTs & Tries** below. It describes the **min/max-bounds** approach, `valid(node, lo, hi)` with `lo < node.val < hi`, which is equally accepted.

*Follow-up:*
- **"Bounds approach?"** Write it and compare. It's also O(n), and it doesn't depend on traversal order.
- **"Iterative?"** Do the in-order walk with an explicit stack. That avoids JS's recursion limit on a degenerate, linked-list-shaped tree of 10k+ nodes.
- **Recover BST:** two nodes have been swapped, and the in-order sequence reveals the two out-of-place values.
- **"Duplicates allowed on one side?"** Clarify first, then change `<=` to `<` for that side.

**Q28. Kth Smallest Element in a BST** *(Amazon, Google, Microsoft)* — tree `[5,3,6,2,4,null,7]`, `k = 3` → `4`

Return the k-th smallest value (1-indexed) in a BST.

- An in-order traversal visits a BST's values in sorted order.
- Count nodes as they're visited, and record the value when the count reaches k.
- Stop as soon as the answer is found.

```js
function kthSmallest(root, k) {
  let count = 0;
  let answer = null;                             // C++ uses -1 as "not found" (see source note)
  function inorder(node) {
    if (!node || answer !== null) return;        // early termination once found
    inorder(node.left);
    if (answer !== null) return;                 // found in the left subtree — stop here too
    count++;
    if (count === k) {
      answer = node.val;
      return;
    }
    inorder(node.right);
  }
  inorder(root);
  return answer;
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
class Solution {
private:
    int count = 0;
    int answer = -1;

    void inorder(TreeNode* root, int k) {
        if (!root || answer != -1) return;

        inorder(root->left, k);
        count++;

        if (count == k) {
            answer = root->val;
            return;
        }
        inorder(root->right, k);
    }
public:
    int kthSmallest(TreeNode* root, int k) {
        inorder(root, k);
        return answer;
    }
};
```

</details>

**Complexity:** O(h + k) time, because it stops after the k-th in-order node. That's O(n) in the worst case, which is what the source states. O(h) space for the recursion stack.

```text
        5
       / \
      3   6
     / \   \
    2   4   7
in-order: 2 (count 1) → 3 (2) → 4 (3 = k) → answer 4, stop
```

💡 *FAANG tip:* In-order traversal is the key pattern for any "k-th smallest / k-th largest" problem in a BST. Use early termination when the answer is found to save time.

*Source note:*
1. **The dry run over-counts.** It shows nodes 5, 6 and 7 visited with counts 4, 5 and 6 "(already found)". In fact, the `answer != -1` guard stops 6 and 7 from being visited at all. Only node 5 is still counted, wastefully, because the C++ doesn't re-check after returning from the left subtree. The JS adds that second check.
2. **`-1` is an ambiguous sentinel** if −1 can be a real value. In that case the result is still right, but early termination is lost. LeetCode constrains `0 ≤ val`, so it's safe there; the JS uses `null` instead.
3. **State isn't reset between calls.** `count` and `answer` are class members that are never reset, so calling `kthSmallest` twice on the same `Solution` object returns the stale first answer. The JS keeps its state per call (tested).

*See also:* the "in-order visits values in sorted order" bullet under **Trees, BSTs & Tries** below.

*Follow-up:* LeetCode's official follow-up asks, "What if the BST is modified often and you query the k-th smallest often?" **Augment each node with its subtree size** (an order-statistic tree). Then:
- If `k ≤ size(left)`, go left.
- If `k == size(left) + 1`, this node is the answer.
- Otherwise, go right with `k − size(left) − 1`.

Each query is O(h), and keeping the sizes up to date costs O(h) per insert or delete.

Two more variants:
- **"Iterative?"** Run the in-order walk with an explicit stack and stop after k pops.
- **"K-th *largest*?"** Use reverse in-order (right, node, left).

**Q29. Serialize and Deserialize Binary Tree** *(Amazon, Google, Microsoft)* — tree `[1,2,3,4,5,null,6]` ↔ `"1,2,4,#,#,5,#,#,3,#,6,#,#"`

Design `serialize` (tree → string) and `deserialize` (string → the identical tree).

- **Serialize:** do a pre-order traversal (root, left, right). Write each value, plus a `#` marker for every null child, with a separator between tokens.
- **Deserialize:** split the string into tokens and rebuild recursively in the same pre-order. Take a token: `#` means null; otherwise create the node, then build its left subtree, then its right.
- The null markers are what make the encoding unambiguous. Pre-order values *without* them can't tell a left child from a right child.

```js
class Codec {
  // Encodes a tree to a single string: preorder, '#' marks null
  serialize(root) {
    const res = [];
    const helper = (node) => {
      if (!node) { res.push('#'); return; }
      res.push(String(node.val));
      helper(node.left);
      helper(node.right);
    };
    helper(root);
    return res.join(',');
  }
  // Decodes the string back into the same tree
  deserialize(data) {
    const tokens = data.split(',');
    let i = 0;                                   // read pointer instead of a queue (shift() is O(n))
    const helper = () => {
      if (i >= tokens.length) return null;
      const token = tokens[i++];
      if (token === '#' || token === '') return null;
      const node = new TreeNode(Number(token)); // C++: stoi(token)
      node.left = helper();                      // same order as serialize: root, left, right
      node.right = helper();
      return node;
    };
    return helper();
  }
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
class Codec {
public:
    // Encodes a tree to a single string.
    string serialize(TreeNode* root) {
        string res;
        serializeHelper(root, res);
        return res;
    }
    void serializeHelper(TreeNode* node, string &res) {
        if (!node) { res += "#,"; return; }
        res += to_string(node->val) + ",";
        serializeHelper(node->left, res);
        serializeHelper(node->right, res);
    }
    // Decodes your encoded data to tree.
    TreeNode* deserialize(string data) {
        queue<string> q;
        string token;
        stringstream ss(data);
        while (getline(ss, token, ',')) q.push(token);
        return deserializeHelper(q);
    }
    TreeNode* deserializeHelper(queue<string> &q) {
        if (q.empty()) return nullptr;
        string token = q.front(); q.pop();
        if (token == "#" || token == "") return nullptr;
        TreeNode* node = new TreeNode(stoi(token));
        node->left = deserializeHelper(q);
        rode->right = deserializeHelper(q);
    }   return node;
};
```

</details>

**Complexity:** O(n) time, since each node is written and read once. O(n) space for the string and tokens, plus O(h) for the recursion stack.

```text
        1
       / \
      2   3
     / \   \
    4   5   6
pre-order with null markers:
1 → 2 → 4 → # → # → 5 → # → # → 3 → # → 6 → # → #
serialized: "1,2,4,#,#,5,#,#,3,#,6,#,#"
deserialize reads the tokens in the same order:
1 (root), 2 (1.left), 4 (2.left), #, #, 5 (2.right), #, #, 3 (1.right), #, 6 (3.right), #, #
```

💡 *FAANG tip:* Pre-order with a null marker is the most common approach. Make sure your serialisation is unambiguous by using separators or markers.

*Source note:*
1. **It won't compile as printed.** `rode->right` is a typo for `node->right`. Also, the closing `}` of `deserializeHelper` is printed *before* `return node;`, which puts the `return` outside the function.
2. **The real output has a trailing comma.** The C++ appends `","` after *every* token, so it actually produces `"…,6,#,#,"`, while the source displays the string without one. The JS joins with `,` (no trailing comma) but also accepts the C++ format (tested).
3. **The space explanation is off.** It says "recursion stack + queue stores up to n nodes", but only the token queue is O(n); the recursion stack is O(h).

*JS note:* the C++ consumes a `queue<string>`. Translating that to `tokens.shift()` would make deserialisation O(n²), so the JS uses a read index instead. `Number(token)` replaces `stoi`. Both directions are recursive, so a degenerate tree deeper than roughly 10k nodes can overflow the JS call stack. Switch to an explicit stack in that case (a 3,000-deep chain round-trips fine in the tests).

*See also:* the reconstruction and serialisation bullet under **Trees, BSTs & Tries** below. It's the same skill as (de)serialising a component tree or a nested JSON config.

*Follow-up:*
- **"Use BFS / LeetCode's format instead?"** Serialise level order with `null` markers and trim the trailing nulls.
- **Serialize and Deserialize BST** (LC 449): no null markers are needed, because pre-order plus the BST ordering bounds is enough to rebuild the tree. That makes it more compact.
- **"N-ary tree?"** Write each node's child count after its value.
- **"Why not `JSON.stringify`?"** It works for plain nested objects, but it's verbose, it fails on cycles and shared references, and the interviewer wants to see you *design* the encoding.

**Q30. Diameter of Binary Tree** *(Amazon, Google, Microsoft)* — tree `[1,2,3,4,null,5,6,null,null,7]` → `5` (path `4-2-1-3-5-7`)

Return the diameter: the number of **edges** on the longest path between any two nodes. The path doesn't have to pass through the root.

- A DFS returns each node's height, counted in nodes.
- At every node, the longest path that *bends* there has `leftHeight + rightHeight` edges. Update a global maximum with it.
- Return `1 + max(left, right)` upwards, because a parent can only extend one side of a child's path.

```js
function diameterOfBinaryTree(root) {
  let maxDia = 0;
  function height(node) {                        // height in NODES; left + right = EDGES through node
    if (!node) return 0;
    const left = height(node.left);
    const right = height(node.right);
    maxDia = Math.max(maxDia, left + right);     // longest path that bends at this node
    return 1 + Math.max(left, right);
  }
  height(root);
  return maxDia;                                 // number of edges
}
```

<details><summary>Original C++ (from source)</summary>

```cpp
class Solution {
private:
    int maxDia;

    int height(TreeNode* node) {
        if (!node) return 0;
        int left = height(node->left);
        int right = height(node->right);
        // path through this node
        maxDia = max(maxDia, left + right);
        return 1 + max(left, right);
    }
public:
    int diameterOfBinaryTree(TreeNode* root) {
        maxDia = 0;
        height(root);
        return maxDia;          // number of edges
    }
};
```

</details>

**Complexity:** O(n) time (each node visited once), O(h) space for the recursion stack.

```text
          1
        /   \
       2     3
      /     / \
     4     5   6
          /
         7
post-order  L  R  maxDia        returns height
4           0  0  max(0,0)=0    1
2           1  0  max(0,1)=1    2
7           0  0  1             1
5           1  0  max(1,1)=1    2
6           0  0  1             1
3           2  1  max(1,3)=3    3
1           2  3  max(3,5)=5    4
→ diameter = 5 edges (4-2-1-3-5-7)
```

💡 *FAANG tip:* Return the height while updating a global diameter. The diameter is measured in edges, so don't add +1 when updating `maxDia`, because `left + right` already counts edges.

*Source note:* the source's example tree diagram leaves out node **7**, yet it claims the longest path is `4-2-1-3-5-7` with 5 edges, and its dry run uses node 7. With the tree exactly as drawn, the diameter would be **4** (`4-2-1-3-5`); both cases are in the tests. The dry run also skips visiting node **6**, which node 3 needs for `right = 1`. The tree above includes 7, and the trace includes 6.

*See also:* the "state what a single call returns" advice under **Trees, BSTs & Tries** below. This problem is the textbook example of it.

*Follow-up:* the same "return one side upwards, record both sides" template solves:
- **Binary Tree Maximum Path Sum** (LC 124): clamp negative branches with `Math.max(0, …)`.
- **Balanced Binary Tree:** return −1 as soon as a subtree is unbalanced.
- **Longest Univalue Path.**

Other common twists:
- **Diameter in *nodes*:** add 1 to the result.
- **Return the path itself:** also return the deepest node on each side.
- **Diameter of a general tree or graph:** run BFS twice. First find the node `u` farthest from any starting node, then find the node farthest from `u`.

**Pattern Cheat Sheet (Top 30):**

```text
Q#   Problem                            Pattern                                    Time          Space
Q1   Two Sum                            Hash map complement lookup                 O(N)          O(N)
Q2   Best Time to Buy & Sell Stock      Greedy running min (= Kadane on diffs)     O(N)          O(1)
Q3   Maximum Subarray                   Kadane: extend or restart                  O(N)          O(1)
Q4   Product of Array Except Self       Prefix × suffix in the output array        O(N)          O(1) extra
Q5   Merge Intervals                    Sort by start + linear sweep               O(N log N)    O(N)
Q6   Rotate Array                       Three reversals                            O(N)          O(1)
Q7   Valid Anagram                      26-slot frequency count                    O(N)          O(1)
Q8   Longest Substring w/o Repeating    Sliding window + last-index map            O(N)          O(min(N,K))
Q9   Longest Palindromic Substring      Expand around 2n-1 centres                 O(N²)         O(1)*
Q10  Group Anagrams                     Frequency-vector hash key                  O(N·K)        O(N·K)
Q11  Reverse Linked List                prev/curr/next pointer flip                O(N)          O(1)
Q12  Linked List Cycle                  Floyd fast/slow pointers                   O(N)          O(1)
Q13  Merge Two Sorted Lists             Dummy head + splice                        O(m+n)        O(1)
Q14  Remove Nth Node From End           Dummy + n-gap two pointers                 O(L)          O(1)
Q15  Detect Cycle (→ cycle start)       Floyd + restart-from-head phase            O(N)          O(1)
Q16  Intersection of Two Lists          Two pointers swap heads at the end         O(m+n)        O(1)
Q17  Add Two Numbers                    Digit-by-digit carry, dummy head           O(max(m,n))   O(1) aux
Q18  Merge K Sorted Lists               Min-heap of k heads (or divide & conquer)  O(N log k)    O(k)
Q19  LRU Cache                          Hash map + doubly linked list              O(1) per op   O(capacity)
Q20  Word Ladder                        BFS by level, mark visited on enqueue      O(N·M²)       O(N·M)
Q21  Trapping Rain Water                Two pointers, move the smaller side        O(N)          O(1)
Q22  Top K Frequent Elements            Count + bucket sort by frequency           O(N)          O(N)
Q23  Product Except Self (arrays)       Explicit prefix[] / suffix[] arrays        O(N)          O(N)
Q24  Longest Consecutive Sequence       Hash set, expand only from run starts      O(N)          O(N)
Q25  Level Order Traversal              BFS with a levelSize snapshot              O(N)          O(W)
Q26  LCA of Binary Tree                 DFS: both sides non-null → fork            O(N)          O(H)
Q27  Validate BST                       In-order must be strictly increasing       O(N)          O(H)
Q28  Kth Smallest in BST                In-order count with early stop             O(H+k)        O(H)
Q29  Serialize/Deserialize Tree         Pre-order + null markers                   O(N)          O(N)
Q30  Diameter of Binary Tree            Return height, record left+right           O(N)          O(H)
* Q9 as written is O(N) space (substring copies); O(1) if you track indices instead.
  W = max tree width, H = tree height, K = charset size (Q8) / avg string length (Q10), M = word length.
```

## Stacks, Queues & Monotonic Structures

```text
Monotonic Stack: Input ➔ push index ➔ next element breaks the invariant? ➔ pop & resolve (compute answer for popped index) ➔ push current
```

- 🏗️ Valid Parentheses and Evaluate Reverse Polish Notation are the canonical stack problems: LIFO order naturally matches "must close in the reverse order they opened" (bracket matching) and "operators apply to the most recently seen operands" (postfix evaluation). Recognizing "this needs to remember what came immediately before, in reverse" is the trigger for reaching for a stack over an array.
- 📉 Monotonic stacks (Daily Temperatures, Largest Rectangle in Histogram) are the O(N) upgrade over an O(N²) "compare every element to every other element" scan. The stack holds indices in increasing (or decreasing) order of value; the moment a new element breaks that order, you pop and resolve every element it invalidates in one pass — each element is pushed and popped at most once, which is what keeps it linear despite the nested-looking `while` inside a `for`.

**Senior Perspective:**
- Monotonic stack is a pattern interviewers specifically probe for because the brute-force version is an "obvious" O(N²) that most candidates write first — flagging it and immediately proposing the stack-based O(N) rewrite is a strong senior signal.
- Frontend tie-in: undo/redo stacks, browser history (LIFO-ish back/forward navigation), and CSS specificity/z-index resolution during style computation all lean on stack-shaped reasoning.

## Linked Lists

```text
Fast/Slow Pointers: head ➔ slow+=1, fast+=2 ➔ fast reaches null (find middle) or fast==slow (cycle detected)
```

- 🏗️ Reversal (in-place, O(1) space, three-pointer `prev/current/next` walk) is the base primitive that composes into harder problems: reverse a sublist between positions `left` and `right`, reorder a list into a front/back zigzag (find middle → reverse second half → zip-merge the two halves), and check if a list is a palindrome (same find-middle-reverse-compare composition). Interviewers stack these because each one is "reversal plus one more idea," and showing you can compose known primitives instead of inventing a new algorithm from scratch is exactly the senior move.
- 🏗️ Floyd's Cycle Detection (slow/fast "tortoise and hare" pointers) solves cycle detection, finding the middle node, and — by extension — palindrome checking, all with O(1) space and no auxiliary hash set. The same pointer-speed-differential idea also finds the intersection point of two singly linked lists by redirecting each pointer to the other list's head once it hits null, forcing both to traverse the same total distance.
- ⚖️ Merging/sorting linked lists (merge two sorted lists, merge sort on a list in O(N log N)) uses a dummy-head node to avoid special-casing "is this the new head?" — a small readability trade that eliminates a whole class of off-by-one bugs. Sorting a linked list specifically favors merge sort over quicksort because linked lists have no random access (`O(N)` to reach an arbitrary index), which kills quicksort's partition-swap efficiency.
- 🏗️ Structural manipulation problems (delete a node given only a reference to it — overwrite its value with the next node's and splice past it; partition a list around a value using two dummy sub-lists then splicing them together; add two numbers stored digit-by-digit with carry propagation; copy a list with random pointers via a node→clone hash map; flatten a multilevel doubly linked list by wiring each child's tail back into the main chain) are all variations on "rewire pointers without losing track of the rest of the list" — the discipline is always: save what you need before you overwrite it.
- 🏗️ Converting a sorted linked list into a height-balanced BST reuses the find-the-middle trick as the recursive root-selection step — a direct example of how one primitive (fast/slow pointers) keeps resurfacing across "unrelated" problems.

**Senior Perspective:**
- Linked-list problems are really pointer-discipline problems — the senior tell is narrating "what do I lose if I overwrite this reference right now?" before writing the mutation.
- These rarely map directly to frontend UI work, but the underlying discipline (careful state mutation without losing references, dummy/sentinel nodes to simplify edge cases) directly parallels writing reducers and linked state-update chains without introducing stale closures or lost references.
- If asked "why not just use an array," the honest answer is O(1) insertion/deletion at a known position without shifting — which is why LRU caches, undo stacks, and some virtualized-list buffer implementations use a doubly linked list under the hood.

## Trees, BSTs & Tries

```text
DFS (recursive):  node ➔ null? return ➔ process (pre/in/post) ➔ recurse left ➔ recurse right
BFS (level order): queue=[root] ➔ pop level, record values, enqueue children ➔ repeat until queue empty
```

- 🏗️ Depth-first traversal (recursive or iterative-with-an-explicit-stack) underlies max depth, pre/in/post-order traversal, path sum, tree diameter, symmetric-tree checking (mirror two subtrees simultaneously), invert tree, and subtree-of-another-tree (DFS to find a candidate root, then a strict tree-equality DFS at that root). Breadth-first traversal (queue-based) underlies level-order traversal, right-side-view (keep the last node processed per level), zigzag level order (alternate append/prepend direction per level), and rotting-oranges-style multi-source spread simulations.
- 🏗️ Binary Search Trees add one extra invariant DFS exploits: validate-BST needs min/max *bound* propagation (not just comparing a node to its immediate children, which misses violations from grandchildren), inorder traversal visits values in sorted order for free (kth-smallest-in-BST), and LCA-in-a-BST can skip recursion entirely by walking down while comparing values against the search range — an O(H) iterative solution instead of a general O(N) tree search. LCA-in-a-general-binary-tree (no ordering to exploit) needs the full recursive "both sides return non-null → I'm the fork" approach instead.
- 🏗️ Reconstruction and serialization problems (build a tree from preorder+inorder arrays using a value→index hash map to find split points in O(1), serialize/deserialize via preorder DFS with null markers, convert a sorted array to a height-balanced BST by always picking the middle element as root, populate next-right-pointers level by level using already-established sibling links to achieve O(1) space instead of a queue) are where "understand recursion deeply enough to reconstruct state from a flattened representation" gets tested directly — this is functionally the same skill as deserializing a component tree or a nested JSON config into a working data structure.
- 🏗️ A Trie (prefix tree) trades memory (one node per shared character prefix) for O(L) insert/search/prefix-check time independent of dictionary size, where L is the query string length — this is the textbook data structure behind autocomplete and search-as-you-type. Word Search on a grid pairs Trie-style prefix pruning (or plain backtracking) with DFS plus a temporary "visited" marker on the board itself to avoid revisiting a cell mid-path.

**Senior Perspective:**
- Recursive tree problems: always state the base case and what a single call is responsible for returning — "this call returns the depth of its subtree" — before writing the recursion; that framing is what makes composition (diameter, balance checks) obvious instead of magic.
- Trie is the single most frontend-relevant structure in this cluster: search-as-you-type, tag/command autocomplete, and fuzzy-file-finders (like a command palette) are all "insert a dictionary into a trie once, then walk it in O(query length) per keystroke" instead of re-filtering the whole list on every character.
- BFS/level-order thinking maps directly onto rendering a component tree level-by-level or computing layout passes that depend on parent-before-child ordering.

## Graphs — BFS/DFS, Topological Sort & Union-Find

```text
Topological Sort (Kahn's/BFS):  build adjacency list + in-degree count ➔ queue all in-degree-0 nodes ➔ pop, "complete" it, decrement neighbors' in-degree ➔ in-degree hits 0? enqueue ➔ done count == N? no cycle
Union-Find: find(x) walks to root ➔ union(a,b) links roots ➔ same root already? adding this edge creates a cycle
```

- 🏗️ BFS explores level-by-level via a queue and is the right tool whenever you need the *shortest* path/number of steps in an unweighted graph or grid (number of islands' connected-component counting also works with DFS, but rotting-oranges' "minutes until every orange rots" specifically needs multi-source BFS — seeding the queue with *every* initially-rotten orange at once, not one at a time, so each BFS "level" corresponds to exactly one minute). DFS explores as deep as possible before backtracking and is the natural fit for exhaustive connectivity checks (flood-filling/"sinking" an island), cloning a graph (with a visited-node hash map to handle cycles in an undirected graph), and grid-based path search with backtracking (word search).
- 🏗️ Topological sort via Kahn's algorithm (BFS + in-degree counting) is the direct answer to "can these tasks be ordered given dependency constraints" (course schedule): build an adjacency list and in-degree array, seed the queue with zero-dependency nodes, and process — if you can't process every node, a cycle exists and the ordering is impossible. This is precisely the algorithm behind dependency resolution in module bundlers and build systems, and it's the same "peel off nodes with no unresolved dependencies" logic used for CSS/style dependency graphs.
- 🏗️ Union-Find (Disjoint Set) answers "are these two nodes already connected" in near-O(1) amortized time via a `find`-the-root/`union`-two-roots pair of operations — it's the standard tool for detecting a redundant edge that creates a cycle in an otherwise-tree-shaped graph, and for validating that a given edge list actually forms a valid tree (exactly N-1 edges, no cycles, i.e., no edge whose two endpoints already share a root).
- 🏗️ Pacific Atlantic Water Flow inverts the naive approach: instead of simulating water flowing downhill from every cell (expensive), it runs DFS *uphill* from each ocean's border cells, marking everywhere water could have reached that ocean — then intersects the two reachability sets. This "flip the direction of the simulation" reframe is a recurring senior-level move whenever brute force means starting a search from every cell individually.

**Senior Perspective:**
- The first question on any graph problem should be "BFS or DFS, and why" — shortest-path/level-based problems want BFS; exhaustive/connectivity/backtracking problems want DFS; dependency-ordering problems want topological sort; "are these already connected / does this edge create a cycle" problems want Union-Find.
- Topological sort is directly relevant to frontend build tooling (bundler dependency graphs) and to sequencing async data-fetching waterfalls where one request depends on another's result.
- Multi-source BFS (rotting oranges) is the same shape as "seed a cache invalidation wave from multiple changed nodes simultaneously" — useful framing when discussing how a state-management library propagates updates through a dependency graph of derived/computed values.

## Recursion, Backtracking & Combinatorics

```text
Backtracking: choose a candidate ➔ recurse deeper ➔ hit a base case (record result) or dead end ➔ undo the choice ➔ try the next candidate
```

- 🏗️ Backtracking is DFS with an explicit "undo" step — generate-parentheses (track open/close counts, only close when valid), permutations (track used elements, swap in/swap out), subsets/power-set (include-or-skip each element at each recursion depth), combination-sum (allow revisiting the same candidate by not advancing the start index, since reuse is permitted), N-Queens (track occupied columns and both diagonals in O(1) sets to prune invalid placements immediately instead of checking the whole board), and palindrome partitioning (only recurse into a split if the prefix is itself a palindrome) all follow the identical "choose → recurse → un-choose" skeleton with a different validity check and a different base case.
- ⚖️ Backtracking's cost is inherently exponential in the worst case (it's exploring a decision tree) — the entire value of the pattern is in *pruning* branches early (N-Queens' O(1) attack-line checks, palindrome-partitioning's early-exit on an invalid prefix) rather than generating every possibility and filtering afterward. Naming the pruning strategy out loud is what separates "I know backtracking" from "I can make backtracking fast enough to matter."

**Senior Perspective:**
- Backtracking is rarely asked as a pure "recite N-Queens" exercise at senior level — the value is recognizing when a UI feature (form-builder with exclusion constraints, multi-select filter combinations, drag-and-drop layout validity checks) is secretly a constraint-satisfaction/backtracking problem in disguise.
- Always state the branching factor and depth before writing code — that's your informal complexity estimate and it tells the interviewer you're thinking about whether this approach will actually terminate in reasonable time on real input sizes.

## Dynamic Programming

```text
Bottom-Up DP: define dp[i] = answer for subproblem i ➔ base case(s) ➔ dp[i] built from dp[i-1], dp[i-2], ... ➔ answer = dp[n]
```

- 🏗️ 1D DP problems reduce to "what's the best decision at position i, given the best decisions at earlier positions" — climbing stairs and Fibonacci (dp[i] = dp[i-1] + dp[i-2], and note climbing-stairs is *literally* Fibonacci in disguise), house robber (rob this house + dp[i-2], or skip it and keep dp[i-1]), coin change (minimum coins for amount `a` = 1 + minimum coins for `a - coin`, minimized over all coin denominations), word break (dp[i] true if some earlier split point dp[j] was true *and* the substring between is a dictionary word), and decode-ways (dp[i] sums contributions from valid 1-digit and 2-digit decodings ending at i) all follow this shape, and all can drop from O(N) space to O(1) by keeping only the last one or two dp values instead of a full array.
- 🏗️ 2D DP problems track two independent dimensions — longest common subsequence and edit distance (Levenshtein distance) both build an (m+1)×(n+1) grid where dp[i][j] compares the two strings' i-th and j-th prefixes; unique paths (grid movement, dp[r][c] = dp[r-1][c] + dp[r][c-1]) and triangle-minimum-path-sum (collapse bottom-up into the row above, achieving O(1) extra space by mutating the input) are the geometric variant of the same idea. Regular expression matching is 2D DP's hardest common form: `*` requires considering "zero copies of the preceding element" and "one-or-more copies" as two separate transitions into the same cell.
- ⚖️ Longest Increasing Subsequence at O(N²) (dp[i] = longest LIS ending at i, comparing against every earlier index) is the version worth explaining clearly; there's a well-known O(N log N) patience-sorting/binary-search refinement, and naming that it exists — even if you implement the O(N²) version under time pressure — signals awareness of the ceiling on how far this pattern can be optimized.
- ⚖️ 0/1 Knapsack-shaped problems (partition equal subset sum, perfect squares) trade a straightforward but incorrect "just iterate forward" implementation for a specific iteration order: partition-equal-subset-sum's inner loop must run *backwards* over the target sum, because iterating forward would let the same number be reused multiple times in one subset, which the 0/1 (use-each-item-at-most-once) constraint forbids.
- 🏗️ Greedy algorithms are DP's cheaper sibling when a locally-optimal choice is provably globally optimal: jump game (track the farthest index reachable so far, fail only if the current index outpaces it) and jump game II (increment a jump counter only when you exhaust the current jump's reachable range) both avoid DP's O(N²) entirely by proving greed suffices — always justify *why* greedy is safe here, since it isn't always.

**Senior Perspective:**
- DP interviews are really "can you define the recurrence relation and base case out loud before writing any code" — the code is almost mechanical once the recurrence is right, so narrate the recurrence first.
- Explicitly call out when you're collapsing a 2D DP table to a rolling 1D array (or a full DP array down to two variables) — that's the concrete "I know the naive version works, here's the optimized one" trade-off senior interviewers are listening for.
- Real frontend tie-in: memoized selectors (Reselect-style derived state) are bottom-up DP in disguise — cached subproblem results that get invalidated and recomputed only when their inputs change, exactly like a dp[i] that only recomputes when dp[i-1] changes.

## Sorting, Searching, Heaps & Randomized Structures

```text
Binary Search: left=0, right=n-1 ➔ mid = (left+right)/2 ➔ target found? return : narrow to the half that could contain it ➔ repeat until left > right
```

- 🏗️ Merge sort (guaranteed O(N log N), O(N) extra space, stable) vs. quicksort (average O(N log N), worst-case O(N²) on adversarial/already-sorted input with a naive pivot, but in-place with O(log N) space) is the classic sorting trade-off to narrate: pick merge sort when stability or worst-case guarantees matter (or when sorting a linked list, since it has no random access for quicksort's partitioning), pick quicksort when average-case speed and low memory overhead matter more than worst-case guarantees.
- 🏗️ Binary search is the default whenever input is sorted (or has a "monotonic" true/false boundary, as in first-bad-version, where `isBadVersion` results transition once from false to true). Its variants — search-insert-position, find-minimum/search-in-a-rotated-sorted-array (each half of a rotated array is still individually sorted, so you can always tell which half to keep), find-peak-element (follow the ascending slope, since a `-∞` boundary guarantees a peak exists in that direction), search-a-2D-matrix (treat the grid as one flattened sorted array via index math), and median-of-two-sorted-arrays (binary search *the partition point* itself, not the values, to hit O(log(min(m,n)))) — all reduce a linear scan to a logarithmic one by proving you can always discard half the remaining search space.
- 🏗️ Heaps (priority queues) are the tool whenever you need "the current min/max of a dynamic set" repeatedly — kth-largest-element and kth-largest-in-a-stream use a size-bounded min-heap (pop the smallest whenever the heap exceeds size k, leaving exactly the k largest, whose root is the answer), K-closest-points-to-origin can use the same bounded-heap idea or a straightforward sort-then-slice for simplicity, and median-from-a-data-stream needs *two* balanced heaps (a max-heap for the lower half, a min-heap for the upper half) so the median is always O(1) to read from the two roots.
- ⚖️ O(1)-amortized data structure design (LRU cache reuses `Map`'s guaranteed insertion-order iteration to implement recency tracking without a manual doubly linked list; insert-delete-getRandom-O(1) bridges an array for O(1) random-index access with a hash map for O(1) lookup, swapping a removed element with the array's last element before popping to avoid an O(N) shift) is where "which two data structures do I combine to get O(1) on every operation" gets tested directly — the recurring trick is that no single built-in structure gives you all the O(1) guarantees you need simultaneously.
- ⚖️ Fisher-Yates shuffle trades a naive `sort(() => Math.random() - 0.5)` (which is statistically biased and *not* a uniform shuffle) for a guaranteed-uniform O(N) algorithm: iterate backwards, swap each element with a uniformly random earlier-or-equal index. This is a case where the "obviously simpler" one-liner is measurably wrong, and knowing that is the actual signal.

**Senior Perspective:**
- Binary search variants are extremely high-leverage to have cold — "sorted, or has a monotonic boundary" should trigger it immediately, and the rotated-array/find-peak variants test whether you can adapt the invariant rather than just reciting the textbook version.
- Heap-backed bounded structures (top-K, streaming median) map directly onto real dashboards — "top 10 slowest API calls in the last hour" or "current p50/p95 latency" are literally kth-largest-in-a-stream and median-from-a-data-stream running in production.
- Data-structure-composition questions (LRU cache, RandomizedSet) are effectively mini system-design problems — the interviewer wants to see you pick the *combination* of structures that satisfies every stated constraint, not just the first one that satisfies most of them.

## Intervals, Caching & Frontend-Applied System Design Patterns

```text
LRU Cache (Map-based):  get/put existing key ➔ delete + re-insert (moves it to "most recent" in Map's iteration order) ➔ over capacity? evict the first key in Map.keys()
```

- 🏗️ Interval problems (merge intervals, meeting rooms/meeting rooms II, insert interval) all start with the same move — sort by start time — then sweep once: merging overlapping ranges into one, counting the maximum simultaneous overlap (meeting rooms II sorts start times and end times *separately* and sweeps both with two pointers to find peak concurrency without checking every pair), or splicing a new interval into an already-sorted, already-disjoint list in three phases (everything strictly before, everything overlapping and merged, everything strictly after).
- 🏗️ LRU cache is the textbook example of choosing a data structure that satisfies *every* stated constraint simultaneously: O(1) `get` and `put` rules out a plain sorted array (O(N) reordering) and rules out a plain hash map alone (no recency ordering) — either pair a hash map with a doubly linked list, or, in JavaScript specifically, exploit that `Map` already preserves insertion order and get recency tracking "for free" by deleting and re-inserting a key on every access.
- ⚖️ Debounce and throttle are opposite trade-offs on the same problem — "an event fires more often than I want to react to it." Debounce delays execution until a pause in events (ideal for a search input: wait until the user stops typing before firing the API call — you give up "instant" feedback to save request volume). Throttle guarantees execution at most once per fixed interval regardless of event frequency (ideal for scroll/resize handlers: you give up reacting to every single pixel of movement to guarantee the handler never runs more than, say, 10 times a second).
- 🏗️ An event emitter (`on`/`off`/`emit` backed by an event-name → callback-array map) is the pub-sub primitive underneath most state-management libraries and custom hook systems — implementing it from scratch demonstrates you understand what's actually happening when a component "subscribes" to a store.
- 📉 Virtual scrolling for large lists is a direct, practical application of sliding-window math to the DOM: given item height, viewport height, and current scroll offset, compute `startIndex = floor(scrollTop / itemHeight)` and slice only the visible range (plus a small buffer) out of an in-memory array of arbitrarily many items, rendering a phantom full-height container so the scrollbar behaves correctly. This is the concrete answer to "how would you render a list of a million rows without crashing the tab" — the underlying array can be O(N) in size, but the DOM footprint stays O(viewport size) regardless of N.
- 🏗️ Task scheduling with a concurrency limit (run at most N async operations at once, immediately backfilling from a queue as each one finishes) and small system-design classes like a Twitter-style feed (merge each followed user's timestamp-ordered posts and take the top 10 by time) or a path-based file system (a flat hash map keyed by full path string, validating that a parent path already exists before allowing a child path to be created) are where DSA fundamentals — queues, hash maps, sorting by a timestamp — compose into something that looks like a mini system-design interview.

**Senior Perspective:**
- This cluster is the most directly "translatable" one in the whole pillar — every item here (debounce, LRU, virtual scroll, event emitter) is something you've plausibly already shipped, so lean on real production war stories instead of abstract algorithm talk.
- ⚖️ Debounce/throttle/LRU-cache-size choices are product decisions disguised as algorithm decisions — the "right" debounce delay or cache size depends on measured user behavior and memory budget, not a universal constant, and saying that out loud shows product judgment layered on top of the technical mechanism.
- When asked to "design X" in a DSA-adjacent frontend interview, default to naming the underlying data structure combination first (hash map + doubly linked list for LRU, two heaps for a running median, sorted-by-start-time sweep for intervals) — that's the load-bearing decision everything else hangs off of.

**Predictive Interview Questions (Algorithms & Problem Solving):**
1. You need to render a chat message list that could grow to hundreds of thousands of messages without the tab freezing. Walk through how you'd combine a sliding-window/virtual-scroll approach with a data structure choice for the underlying message store, and explain the complexity trade-offs of each option you consider.
2. A user reports that autocomplete suggestions lag noticeably after the list of possible matches grows past a few thousand entries. Diagnose the likely algorithmic cause, propose a fix (trie vs. debounced filtering vs. both), and explain why you'd pick one over the other given the constraint that suggestions must update on every keystroke.
3. Tell me about a time you identified and fixed a real performance bottleneck in production that traced back to an inefficient algorithm or data structure choice — what was the original complexity, what did you change it to, how did you measure the impact, and how did you communicate the trade-off to your team before shipping the fix?

**Executive Summary Cheat Sheet:** Recognize the pattern first (two-pointer/sliding window for arrays, BFS/DFS/Union-Find for graphs, DP for overlapping subproblems, heaps for streaming top-K) and always state the time/space trade-off you're accepting before writing code. Every core pattern maps to a real frontend primitive — sliding window is virtualization, tries are autocomplete, hash-map-plus-linked-structure is an LRU cache, debounce/throttle are opposite trade-offs on event frequency, and topological sort is bundler dependency resolution.
