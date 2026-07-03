'use strict';

/**
 * A dependency-free collection of small, pure utility functions.
 *
 * Every function here is deterministic, validates its inputs, and has no side
 * effects, so each one can be reasoned about and unit tested in isolation.
 */

// ---------------------------------------------------------------------------
// String helpers
// ---------------------------------------------------------------------------

/**
 * Capitalize the first character of a string.
 * @param {string} value
 * @returns {string}
 */
function capitalize(value) {
  if (typeof value !== 'string' || value.length === 0) {
    return '';
  }
  return value.charAt(0).toUpperCase() + value.slice(1);
}

/**
 * Lowercase the first character of a string.
 * @param {string} value
 * @returns {string}
 */
function decapitalize(value) {
  if (typeof value !== 'string' || value.length === 0) {
    return '';
  }
  return value.charAt(0).toLowerCase() + value.slice(1);
}

/**
 * Convert a string to kebab-case.
 * @param {string} value
 * @returns {string}
 */
function toKebabCase(value) {
  return String(value)
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
}

/**
 * Convert a string to snake_case.
 * @param {string} value
 * @returns {string}
 */
function toSnakeCase(value) {
  return String(value)
    .replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase();
}

/**
 * Convert a delimited string to camelCase.
 * @param {string} value
 * @returns {string}
 */
function toCamelCase(value) {
  return String(value)
    .replace(/[-_\s]+(.)?/g, (_, chr) => (chr ? chr.toUpperCase() : ''))
    .replace(/^(.)/, (chr) => chr.toLowerCase());
}

/**
 * Truncate a string to a maximum length, appending an ellipsis when cut.
 * @param {string} value
 * @param {number} maxLength
 * @returns {string}
 */
function truncate(value, maxLength) {
  const text = String(value);
  if (text.length <= maxLength) {
    return text;
  }
  return text.slice(0, Math.max(0, maxLength - 3)) + '...';
}

/**
 * Reverse the characters of a string.
 * @param {string} value
 * @returns {string}
 */
function reverseString(value) {
  return Array.from(String(value)).reverse().join('');
}

/**
 * Determine whether a string is a palindrome, ignoring case and punctuation.
 * @param {string} value
 * @returns {boolean}
 */
function isPalindrome(value) {
  const normalized = String(value).toLowerCase().replace(/[^a-z0-9]/g, '');
  return normalized === Array.from(normalized).reverse().join('');
}

/**
 * Count how many times a substring appears in a string.
 * @param {string} value
 * @param {string} search
 * @returns {number}
 */
function countOccurrences(value, search) {
  if (!search) {
    return 0;
  }
  return String(value).split(search).length - 1;
}

/**
 * Escape HTML-sensitive characters in a string.
 * @param {string} value
 * @returns {string}
 */
function escapeHtml(value) {
  const replacements = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  };
  return String(value).replace(/[&<>"']/g, (char) => replacements[char]);
}

// ---------------------------------------------------------------------------
// Array helpers
// ---------------------------------------------------------------------------

/**
 * Split an array into chunks of a given size.
 * @param {Array} items
 * @param {number} size
 * @returns {Array<Array>}
 */
function chunk(items, size) {
  if (size <= 0) {
    return [];
  }
  const result = [];
  for (let index = 0; index < items.length; index += size) {
    result.push(items.slice(index, index + size));
  }
  return result;
}

/**
 * Return a new array with duplicate values removed.
 * @param {Array} items
 * @returns {Array}
 */
function unique(items) {
  return Array.from(new Set(items));
}

/**
 * Group array elements by the key returned from the selector.
 * @param {Array} items
 * @param {(item: any) => string} selector
 * @returns {Object<string, Array>}
 */
function groupBy(items, selector) {
  return items.reduce((groups, item) => {
    const key = selector(item);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {});
}

/**
 * Partition an array into elements that pass and fail a predicate.
 * @param {Array} items
 * @param {(item: any) => boolean} predicate
 * @returns {[Array, Array]}
 */
function partition(items, predicate) {
  const passed = [];
  const failed = [];
  for (const item of items) {
    (predicate(item) ? passed : failed).push(item);
  }
  return [passed, failed];
}

/**
 * Pair up elements from two arrays, stopping at the shorter length.
 * @param {Array} first
 * @param {Array} second
 * @returns {Array<[any, any]>}
 */
function zip(first, second) {
  const length = Math.min(first.length, second.length);
  const result = [];
  for (let index = 0; index < length; index += 1) {
    result.push([first[index], second[index]]);
  }
  return result;
}

/**
 * Flatten an array by a single level.
 * @param {Array} items
 * @returns {Array}
 */
function flattenOnce(items) {
  return items.reduce((flat, item) => flat.concat(item), []);
}

/**
 * Build an array of integers from start (inclusive) to end (exclusive).
 * @param {number} start
 * @param {number} end
 * @returns {number[]}
 */
function range(start, end) {
  const result = [];
  for (let value = start; value < end; value += 1) {
    result.push(value);
  }
  return result;
}

/**
 * Sum the numbers in an array.
 * @param {number[]} numbers
 * @returns {number}
 */
function sum(numbers) {
  return numbers.reduce((total, current) => total + current, 0);
}

/**
 * Compute the arithmetic mean of an array of numbers.
 * @param {number[]} numbers
 * @returns {number}
 */
function average(numbers) {
  if (numbers.length === 0) {
    return 0;
  }
  return sum(numbers) / numbers.length;
}

/**
 * Return the element with the largest value produced by the selector.
 * @param {Array} items
 * @param {(item: any) => number} selector
 * @returns {any}
 */
function maxBy(items, selector) {
  if (items.length === 0) {
    return undefined;
  }
  return items.reduce((best, item) =>
    (selector(item) > selector(best) ? item : best));
}

/**
 * Return the element with the smallest value produced by the selector.
 * @param {Array} items
 * @param {(item: any) => number} selector
 * @returns {any}
 */
function minBy(items, selector) {
  if (items.length === 0) {
    return undefined;
  }
  return items.reduce((best, item) =>
    (selector(item) < selector(best) ? item : best));
}

/**
 * Return the elements present in the first array but not the second.
 * @param {Array} first
 * @param {Array} second
 * @returns {Array}
 */
function difference(first, second) {
  const exclude = new Set(second);
  return first.filter((item) => !exclude.has(item));
}

// ---------------------------------------------------------------------------
// Number and math helpers
// ---------------------------------------------------------------------------

/**
 * Clamp a number between a minimum and maximum.
 * @param {number} value
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

/**
 * Round a number to a fixed number of decimal places.
 * @param {number} value
 * @param {number} decimals
 * @returns {number}
 */
function roundTo(value, decimals) {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
}

/**
 * Determine whether an integer is even.
 * @param {number} value
 * @returns {boolean}
 */
function isEven(value) {
  return value % 2 === 0;
}

/**
 * Determine whether a number is a prime.
 * @param {number} value
 * @returns {boolean}
 */
function isPrime(value) {
  if (!Number.isInteger(value) || value < 2) {
    return false;
  }
  for (let divisor = 2; divisor * divisor <= value; divisor += 1) {
    if (value % divisor === 0) {
      return false;
    }
  }
  return true;
}

/**
 * Compute the greatest common divisor of two integers.
 * @param {number} a
 * @param {number} b
 * @returns {number}
 */
function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y !== 0) {
    [x, y] = [y, x % y];
  }
  return x;
}

/**
 * Compute the least common multiple of two integers.
 * @param {number} a
 * @param {number} b
 * @returns {number}
 */
function lcm(a, b) {
  if (a === 0 || b === 0) {
    return 0;
  }
  return Math.abs(a * b) / gcd(a, b);
}

/**
 * Compute the factorial of a non-negative integer.
 * @param {number} value
 * @returns {number}
 */
function factorial(value) {
  if (!Number.isInteger(value) || value < 0) {
    throw new RangeError('factorial requires a non-negative integer');
  }
  let result = 1;
  for (let current = 2; current <= value; current += 1) {
    result *= current;
  }
  return result;
}

/**
 * Return the nth Fibonacci number (zero-indexed).
 * @param {number} n
 * @returns {number}
 */
function fibonacci(n) {
  let previous = 0;
  let current = 1;
  for (let index = 0; index < n; index += 1) {
    [previous, current] = [current, previous + current];
  }
  return previous;
}

/**
 * Express a numerator as a percentage of a denominator.
 * @param {number} numerator
 * @param {number} denominator
 * @returns {number}
 */
function percentage(numerator, denominator) {
  if (denominator === 0) {
    return 0;
  }
  return (numerator / denominator) * 100;
}

// ---------------------------------------------------------------------------
// Object helpers
// ---------------------------------------------------------------------------

/**
 * Create a copy of an object containing only the given keys.
 * @param {Object} source
 * @param {string[]} keys
 * @returns {Object}
 */
function pick(source, keys) {
  const result = {};
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      result[key] = source[key];
    }
  }
  return result;
}

/**
 * Create a copy of an object excluding the given keys.
 * @param {Object} source
 * @param {string[]} keys
 * @returns {Object}
 */
function omit(source, keys) {
  const exclude = new Set(keys);
  const result = {};
  for (const key of Object.keys(source)) {
    if (!exclude.has(key)) {
      result[key] = source[key];
    }
  }
  return result;
}

/**
 * Transform each value of an object using the given mapper.
 * @param {Object} source
 * @param {(value: any, key: string) => any} mapper
 * @returns {Object}
 */
function mapValues(source, mapper) {
  const result = {};
  for (const key of Object.keys(source)) {
    result[key] = mapper(source[key], key);
  }
  return result;
}

/**
 * Swap the keys and values of an object.
 * @param {Object} source
 * @returns {Object}
 */
function invert(source) {
  const result = {};
  for (const key of Object.keys(source)) {
    result[source[key]] = key;
  }
  return result;
}

/**
 * Determine whether an object has no own enumerable properties.
 * @param {Object} source
 * @returns {boolean}
 */
function isEmptyObject(source) {
  return Object.keys(source).length === 0;
}

/**
 * Safely read a nested value using a dotted path.
 * @param {Object} source
 * @param {string} path
 * @param {any} [fallback]
 * @returns {any}
 */
function getNested(source, path, fallback) {
  const segments = path.split('.');
  let current = source;
  for (const segment of segments) {
    if (current == null || !Object.prototype.hasOwnProperty.call(current, segment)) {
      return fallback;
    }
    current = current[segment];
  }
  return current;
}

// ---------------------------------------------------------------------------
// Date helpers
// ---------------------------------------------------------------------------

/**
 * Return a new date offset by a number of days.
 * @param {Date} date
 * @param {number} days
 * @returns {Date}
 */
function addDays(date, days) {
  const copy = new Date(date.getTime());
  copy.setDate(copy.getDate() + days);
  return copy;
}

/**
 * Count the whole days between two dates.
 * @param {Date} start
 * @param {Date} end
 * @returns {number}
 */
function daysBetween(start, end) {
  const millisPerDay = 24 * 60 * 60 * 1000;
  return Math.floor((end.getTime() - start.getTime()) / millisPerDay);
}

/**
 * Determine whether a date falls on a weekend.
 * @param {Date} date
 * @returns {boolean}
 */
function isWeekend(date) {
  const day = date.getDay();
  return day === 0 || day === 6;
}

/**
 * Return a new date set to the start of the day.
 * @param {Date} date
 * @returns {Date}
 */
function startOfDay(date) {
  const copy = new Date(date.getTime());
  copy.setHours(0, 0, 0, 0);
  return copy;
}

/**
 * Determine whether a year is a leap year.
 * @param {number} year
 * @returns {boolean}
 */
function isLeapYear(year) {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}

// ---------------------------------------------------------------------------
// Validation helpers
// ---------------------------------------------------------------------------

/**
 * Determine whether a string looks like a valid email address.
 * @param {string} value
 * @returns {boolean}
 */
function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value));
}

/**
 * Determine whether a value is a non-empty string.
 * @param {any} value
 * @returns {boolean}
 */
function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

/**
 * Determine whether a value is a positive integer.
 * @param {any} value
 * @returns {boolean}
 */
function isPositiveInteger(value) {
  return Number.isInteger(value) && value > 0;
}

/**
 * Determine whether a number falls within an inclusive range.
 * @param {number} value
 * @param {number} min
 * @param {number} max
 * @returns {boolean}
 */
function isInRange(value, min, max) {
  return value >= min && value <= max;
}

/**
 * Determine whether a string is a canonical v4 UUID.
 * @param {string} value
 * @returns {boolean}
 */
function isUuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    .test(String(value));
}

// ---------------------------------------------------------------------------
// Functional helpers
// ---------------------------------------------------------------------------

/**
 * Return the value passed to it unchanged.
 * @param {any} value
 * @returns {any}
 */
function identity(value) {
  return value;
}

/**
 * Wrap a function so it only runs once; later calls return the first result.
 * @param {Function} fn
 * @returns {Function}
 */
function once(fn) {
  let called = false;
  let result;
  return function wrapped(...args) {
    if (!called) {
      called = true;
      result = fn.apply(this, args);
    }
    return result;
  };
}

/**
 * Memoize a single-argument function using a Map cache.
 * @param {Function} fn
 * @returns {Function}
 */
function memoize(fn) {
  const cache = new Map();
  return function wrapped(arg) {
    if (cache.has(arg)) {
      return cache.get(arg);
    }
    const value = fn.call(this, arg);
    cache.set(arg, value);
    return value;
  };
}

/**
 * Compose functions left to right, feeding each result into the next.
 * @param {...Function} fns
 * @returns {Function}
 */
function pipe(...fns) {
  return function piped(initial) {
    return fns.reduce((value, fn) => fn(value), initial);
  };
}

/**
 * Compose functions right to left, feeding each result into the previous.
 * @param {...Function} fns
 * @returns {Function}
 */
function compose(...fns) {
  return function composed(initial) {
    return fns.reduceRight((value, fn) => fn(value), initial);
  };
}

module.exports = {
  capitalize,
  decapitalize,
  toKebabCase,
  toSnakeCase,
  toCamelCase,
  truncate,
  reverseString,
  isPalindrome,
  countOccurrences,
  escapeHtml,
  chunk,
  unique,
  groupBy,
  partition,
  zip,
  flattenOnce,
  range,
  sum,
  average,
  maxBy,
  minBy,
  difference,
  clamp,
  roundTo,
  isEven,
  isPrime,
  gcd,
  lcm,
  factorial,
  fibonacci,
  percentage,
  pick,
  omit,
  mapValues,
  invert,
  isEmptyObject,
  getNested,
  addDays,
  daysBetween,
  isWeekend,
  startOfDay,
  isLeapYear,
  isEmail,
  isNonEmptyString,
  isPositiveInteger,
  isInRange,
  isUuid,
  identity,
  once,
  memoize,
  pipe,
  compose,
};
