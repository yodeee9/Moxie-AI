import type { NextApiRequest, NextApiResponse } from 'next';

const endpoint = process.env.API_ENDPOINT || '';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { input, session_id } = req.body;

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input,session_id }),
      });
      console.log(response)
      const data = await response.json();
      res.status(200).json({ response: data.response });
      console.log(data.response);
      return data.response;
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}