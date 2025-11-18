/**
 * Example Test
 *
 * Simple test to verify Vitest infrastructure is working
 */

import { describe, it, expect } from 'vitest';

describe('Test Infrastructure', () => {
  it('should run basic math correctly', () => {
    // Simple addition test to verify mathematical operations function as expected
    expect(2 + 2).toBe(4);
  });

  it('should handle string operations', () => {
    // Create a string and verify its properties like length and exact value
    // Demonstrates basic string manipulation and assertion techniques
    const str = 'hello';
    expect(str).toEqual('hello'); // Check exact string match
    expect(str.length).toBe(5);   // Verify string length
  });

  it('should handle arrays', () => {
    // Verify array creation, length, and element containment
    // Shows how to test array properties and element existence
    const arr = [1, 2, 3];
    expect(arr).toHaveLength(3);     // Check total number of array elements
    expect(arr).toContain(2);         // Verify specific element exists
  });

  it('should handle objects', () => {
    // Test object creation and property verification
    // Demonstrates object property checking and value validation
    const obj = { name: 'test', value: 42 };
    expect(obj).toHaveProperty('name');  // Check object has specific property
    expect(obj.value).toBe(42);           // Verify specific property value
  });

  it('should handle async operations', async () => {
    // Demonstrate promise resolution and async testing
    // Shows how to test asynchronous code resolution
    const promise = Promise.resolve('success');
    await expect(promise).resolves.toBe('success');  // Ensure promise resolves correctly
  });
});