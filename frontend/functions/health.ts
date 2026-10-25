import { Handler } from '@netlify/functions';

export const handler: Handler = async () => {
  return {
    statusCode: 200,
    body: JSON.stringify({ 
      status: 'ok', 
      timestamp: new Date().toISOString(),
      environment: process.env.APP_ENV || 'development'
    }),
  };
};

