/// <reference types="node" />

// Ensure Node.js globals are available
declare global {
  var console: Console;
  var process: NodeJS.Process;
  var __dirname: string;
  var __filename: string;
}

export {};

