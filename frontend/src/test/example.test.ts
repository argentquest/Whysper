/**
 * Example Test
 *
 * Simple test to verify Vitest infrastructure is working
 */

import { describe, it, expect } from 'vitest';

describe('Test Infrastructure', () => {
  it('should run basic math correctly', () => {
    expect(2 + 2).toBe(4);
  });

  it('should handle string operations', () => {
    const str = 'hello';
    expect(str).toEqual('hello');
    expect(str.length).toBe(5);
  });

  it('should handle arrays', () => {
    const arr = [1, 2, 3];
    expect(arr).toHaveLength(3);
    expect(arr).toContain(2);
  });

  it('should handle objects', () => {
    const obj = { name: 'test', value: 42 };
    expect(obj).toHaveProperty('name');
    expect(obj.value).toBe(42);
  });

  it('should handle async operations', async () => {
    const promise = Promise.resolve('success');
    await expect(promise).resolves.toBe('success');
  });
});
