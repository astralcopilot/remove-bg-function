// Copyright (C) 2025 Astral
// SPDX-License-Identifier: AGPL-3.0-only

const functions = require('@google-cloud/functions-framework');
const { removeBackground } = require('@imgly/background-removal-node');
const { randomUUID } = require('crypto');
const { unlink, writeFile } = require('fs/promises');
const { tmpdir } = require('os');
const { join } = require('path');
const { pathToFileURL } = require('url');

// Configuration for the background removal
const config = {
  publicPath: pathToFileURL(join(__dirname, './models/')).href,
  output: {
    format: "image/png",
  },
  fetchArgs: {
    mode: "no-cors",
  },
};

// Background removal function
const removeBg = async (imageUrl) => {
  let tempFilePath;
  
  try {
    // Check if input is base64
    if (imageUrl.startsWith("data:image/") || imageUrl.length > 1000) {
      // It's likely base64, save to temp file
      const base64Data = imageUrl.replace(/^data:image\/[a-z]+;base64,/, "");
      const buffer = Buffer.from(base64Data, "base64");
      
      // Create temporary file
      const tempFileName = `temp_${randomUUID()}.png`;
      tempFilePath = join(tmpdir(), tempFileName);
      
      await writeFile(tempFilePath, buffer);
      
      // Use the temp file path
      const blob = await removeBackground(tempFilePath, config);
      const arrayBuffer = await blob.arrayBuffer();
      return Buffer.from(arrayBuffer);
    } else {
      // It's a URL or file path, use directly
      const blob = await removeBackground(imageUrl, config);
      const arrayBuffer = await blob.arrayBuffer();
      return Buffer.from(arrayBuffer);
    }
  } finally {
    // Clean up temporary file
    if (tempFilePath) {
      try {
        await unlink(tempFilePath);
      } catch (error) {
        console.warn("Failed to delete temporary file:", error);
      }
    }
  }
};

// Main background removal function
functions.http('removeBackground', async (req, res) => {
  // Handle CORS
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }
  
  // Health check endpoint
  if (req.method === 'GET') {
    res.status(200).send('Background removal service is healthy!');
    return;
  }
  
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed. Use GET for health check or POST for background removal.' });
    return;
  }
  
  const { imageUrl } = req.body;
  
  if (!imageUrl) {
    res.status(400).json({ error: 'imageUrl is required' });
    return;
  }
  
  try {
    console.log('Processing background removal for:', imageUrl.substring(0, 100));
    
    const buffer = await removeBg(imageUrl);
    
    res.set('Content-Type', 'image/png');
    res.set('Cache-Control', 'public, max-age=3600'); // Cache for 1 hour
    res.status(200).send(buffer);
    
    console.log('Background removal completed successfully');
  } catch (error) {
    console.error('Background removal failed:', error);
    res.status(500).json({
      error: 'Failed to remove background',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});
