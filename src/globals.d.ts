/// <reference types="node" />

// Ensure Node.js globals are available
declare global {
  var console: Console;
  var process: NodeJS.Process;
  var __dirname: string;
  var __filename: string;
  
  // URLSearchParams is available in Node.js 18+
  var URLSearchParams: {
    new (init?: string[][] | Record<string, string> | string | URLSearchParams): URLSearchParams;
    prototype: URLSearchParams;
  };
}

export {};

