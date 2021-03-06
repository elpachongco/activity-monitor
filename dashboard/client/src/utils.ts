/**
 * Contains utility functions
 * No global variables allowed.
 */

import { Activity } from "./types";

/** 
 * Return an array of strings of time in a 24-hour-format day. 
 * Useful for chart labels.
 * @param interval - interval of the times to list in minutes
 * @returns An array of strings containing time. Starts at 12:00:00 AM.
 * @example 
 * ```ts
 *  getTimesInDay(30)
 *  >> ["12:00:00 AM", "12:30:00 AM", ... "11:30:00 PM"]
 * ```
*/
function 
getTimesInDay(interval: number): string[] 
{
	const absInterval = Math.abs(interval);
	let hours: string[] = []
	let dateTime = (new Date()).setHours(0, 0, 0, 0);
	// Convert interval (minutes) to ms
	let intervalMs = (absInterval * 60) * 1000 ;
	const maxMinutesInDay = 1440

	for (let minutes=0; minutes < maxMinutesInDay ; minutes += interval) {
		let time = (new Date(dateTime)).toLocaleTimeString();
		hours.push(time);
		dateTime += intervalMs;
	}

	return hours
}

/** 
 * Return the sum of any given array 
 * @example
 * ```js
 * aSum([-8, 2])
 * >> -6
 * ```
 */
function aSum(a: number[]): number {
	return a.reduce((prevVal: number, currVal: number) => {
		return prevVal + currVal;
	})
};

/**
 * Datetime Indexer
 * Returns range of indexes of rows that fit the given datetime.
 * Tests both `actStart` and `actEnd`.
 * Assumes table is sorted ascending. 
 * 
 * @returns [null, null] if unable to find
 * @returns [number, number] index
 */
function 
dtRangeIndex(table: Activity, start: Date, end: Date = new Date()): 
{from: number | null, to: number | null}
{

	let started = false;
	let ended = false;
	let index: {from:number | null, to:number | null} = {
		from: null,
		to: null
	};
	let i = 0;
	for (let item of table["actStart"]) {
		let actStart = new Date(item); 
		if (actStart >= start && !started){index.from = i; started = !started;};
		if (started && actStart <= end) {index.to = i; ended = !ended;};
		if (ended && actStart > end) break;
		i++;
	};

	// return [startIndex || null, endIndex || null];
	return index;
};


/**
 * Table verfier
 * Checks wether the given table has exactly the same number of rows (array len)
 * for each column (key/prop)
 * @param table - any object with keys and value as Column and row
 */
function isTable(table: any): Boolean
{
	let keys = Object.keys(table); if (keys.length < 1) return false;

	let rowCount = table[keys[0]].length;

	for (const key of keys) 
		if (table[key] != rowCount) return false;

	return true;
}


/**
 * Transforms given Date object with 
 * @param date 
 * @returns `date` but with time set to 00:00:00.00 
 */
function dayStart(date: Date = new Date()): Date
{
	let newDate = date.setHours(0,0,0,0) 
	return new Date(newDate)
}


/**
 * Tests whether obj is in array. Uses Strict equality `===`.
 * @param obj - any 
 * @param arr - 
 * @returns `true` if object found in array
 */
function includes(obj: any, arr: any[]): Boolean
{
	for (let item in arr) {if (obj === item) return true;}
	return false;
}

function getDaysInWeek(): string[] {
	return ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
}



/**
 * Loop through a string and separate its parts with `sep`.  
 * 
 * @param s - string to decompose
 * @param sep - separator, Default is space
 * @param caseSensitive - Whether
 * @returns array of strings from `s` but without the `sep`s
 */
function stringToArray(s: string, re: RegExp | null = null, 
	caseSensitive = false): string[] | null
{
	if (!caseSensitive) s = s.toLowerCase();

	// Default to separating words with spaces. Unicode.
	if (re == null) { re =  /([\u0000-\u0019\u0021-\uFFFF])+/gu } 

	let arr = s.match(re) 

	if (arr == null) {return null}

	return arr
}

/**
 * Return a normalized array from the supplied array `arr`
 * @param arr - Array to normalize
 * @param multiplier - Optional multiplier 
 * @returns - Normalized array.
 */
function normalize(arr: number[], multiplier=1): number[] {
	let max = aMax(arr)
	let min = aMin(arr)


	let normalized: number[] = []
	arr.map((item) => {
		let norm = (item - min) / (max - min)
		normalized.push( Math.round(norm*multiplier) )
	})
	return normalized
}

/**
 * Given an array of numbers, returns the greatest number 
 * @param arr 
 */
function aMax(arr: number[]): number {
	return Math.max(...arr)
}

/**
 * returns the smallest number in an array
 * @param arr 
 * @returns 
 */
function aMin(arr: number[]): number {
	return Math.min(...arr)
}

export {
	getDaysInWeek, 
	getTimesInDay, 
	aSum, 
	includes, 
	dtRangeIndex, 
	isTable, 
	dayStart,
	stringToArray,
	normalize
}