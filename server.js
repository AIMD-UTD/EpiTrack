import express from 'express';
import cors from 'cors';
import { config } from 'dotenv';
import pg from 'pg';

config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const { Pool } = pg;

// Create a connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL?.includes('neon.tech') ? { rejectUnauthorized: false } : false
});

// Format number with commas
function formatNumber(num) {
  return num.toLocaleString('en-US');
}

// Get stats endpoint
app.get('/api/stats', async (req, res) => {
  try {
    const queries = {
      articlesProcessed: 'SELECT COUNT(*)::BIGINT AS count FROM articles;',
      keywordsExtracted: `
        SELECT COUNT(DISTINCT keyword)::BIGINT AS count
        FROM articles,
        LATERAL jsonb_array_elements_text(keywords) AS keyword
        WHERE keywords IS NOT NULL;
      `,
      diseasesTracked: `
        SELECT COUNT(DISTINCT disease)::BIGINT AS count
        FROM articles,
        LATERAL jsonb_object_keys(disease_breakdown) AS disease
        WHERE disease_breakdown IS NOT NULL AND jsonb_typeof(disease_breakdown) = 'object';
      `,
      countriesCovered: `
        SELECT COUNT(DISTINCT country)::BIGINT AS count
        FROM articles
        WHERE country IS NOT NULL AND country != '';
      `
    };

    const results = {};
    
    for (const [key, query] of Object.entries(queries)) {
      const result = await pool.query(query);
      results[key] = parseInt(result.rows[0].count);
    }

    const stats = {
      articlesProcessed: results.articlesProcessed,
      keywordsExtracted: results.keywordsExtracted,
      diseasesTracked: results.diseasesTracked,
      countriesCovered: results.countriesCovered,
      lastUpdated: new Date().toISOString(),
      display: {
        articlesProcessed: formatNumber(results.articlesProcessed),
        keywordsExtracted: formatNumber(results.keywordsExtracted),
        diseasesTracked: formatNumber(results.diseasesTracked),
        countriesCovered: formatNumber(results.countriesCovered)
      }
    };

    res.json(stats);
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
});

// Get recent searches endpoint (based on recently analyzed articles)
app.get('/api/recent-searches', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;
    
    // Get recent articles with disease breakdowns
    const query = `
      SELECT 
        disease_breakdown,
        fetched_at,
        title
      FROM articles
      WHERE disease_breakdown IS NOT NULL 
        AND jsonb_typeof(disease_breakdown) = 'object'
        AND disease_breakdown != '{}'::jsonb
      ORDER BY fetched_at DESC
      LIMIT $1;
    `;

    const result = await pool.query(query, [limit * 2]); // Get more to account for duplicates
    
    const recentSearches = [];
    const seenDiseases = new Set();
    
    for (const row of result.rows) {
      if (!row.disease_breakdown) continue;
      
      // Extract disease names from the breakdown
      const diseases = Object.keys(row.disease_breakdown);
      
      for (const disease of diseases) {
        if (seenDiseases.has(disease.toLowerCase())) continue;
        
        // Format disease name (capitalize first letter of each word)
        const formattedDisease = disease
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ');
        
        // Calculate time ago
        const fetchedAt = new Date(row.fetched_at);
        const now = new Date();
        const diffMs = now - fetchedAt;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        
        let timeAgo;
        if (diffHours >= 24) {
          const days = Math.floor(diffHours / 24);
          timeAgo = `${days}d ago`;
        } else if (diffHours > 0) {
          timeAgo = `${diffHours}h ago`;
        } else if (diffMinutes > 0) {
          timeAgo = `${diffMinutes}m ago`;
        } else {
          timeAgo = 'Just now';
        }
        
        recentSearches.push({
          query: formattedDisease,
          timeAgo: timeAgo,
          timestamp: fetchedAt.toISOString()
        });
        
        seenDiseases.add(disease.toLowerCase());
        
        if (recentSearches.length >= limit) break;
      }
      
      if (recentSearches.length >= limit) break;
    }
    
    res.json(recentSearches);
  } catch (error) {
    console.error('Error fetching recent searches:', error);
    res.status(500).json({ error: 'Failed to fetch recent searches' });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 API server running on http://localhost:${PORT}`);
});

