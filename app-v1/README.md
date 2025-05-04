# Welcome to Remix!

- 📖 [Remix docs](https://remix.run/docs)

## Development

Run the dev server:

```shellscript
npm run dev
```

## Deployment

First, build your app for production:

```sh
npm run build
```

Then run the app in production mode:

```sh
npm start
```

Now you'll need to pick a host to deploy it to.

### DIY

If you're familiar with deploying Node applications, the built-in Remix app server is production-ready.

Make sure to deploy the output of `npm run build`

- `build/server`
- `build/client`

## Styling

This template comes with [Tailwind CSS](https://tailwindcss.com/) already configured for a simple default starting experience. You can use whatever css framework you prefer. See the [Vite docs on css](https://vitejs.dev/guide/features.html#css) for more information.


//   });
//   const GOOGLE_GENAI_API_KEY = 'AIzaSyDkrBwocV7Dr0PWePpmBSb82vQYs4U3L9o';

//   const [name, setName] = useState('')
//   const helloFlow = async () => {
//     // make a generation request
//     const { text } = await ai.generate(`Hello Gemini, my name is ${name}`);
//     console.log(text);
//   }
//   return (
//     <div>
//       <TextField variant='outlined' name='name' value={name} onChange={(e) => {
//         setName(e.target.value)
//       }} />
//       <Button variant="contained"
//         type="button" onClick={helloFlow}>
//       </Button>
//     </div>
//   )
// }

// export default _index


// 'use client';
// import React, { useEffect, useState } from 'react'
// // import the Genkit and Google AI plugin libraries
// import supabase from 'config';
// import { Button, TextField } from '@mui/material';
// import googleAI, { gemini15Flash } from '@genkit-ai/googleai';
// import { genkit } from 'genkit';

// const _index = () => {
//   useEffect(() => {
//     supabase.auth.getUser().then((res) => {
//       console.log(
//         'res', res
//       );

//     })
//   }, [])
//   const ai = genkit({
//     plugins: [googleAI()],
//     model: gemini15Flash, // set default model'use client';



// // Server-side action to handle form submission and AI generation
// export const action = async ({ request }: ActionFunctionArgs) => {
//   try {
//     const formData = await request.formData();
//     const name = formData.get('name')?.toString();

//     if (!name) {
//       return json({ error: 'Name is required' }, { status: 400 });
//     }

//     // Generate text using Genkit
//     // Initialize Genkit server-side (outside component)
// // const genkitConfig = genkit({
// //   plugins: [googleAI({ apiKey: process.env.GOOGLE_GENAI_API_KEY || 'AIzaSyDkrBwocV7Dr0PWePpmBSb82vQYs4U3L9o' })],
// //   model: gemini15Flash,
// // });
// //     const response = await genkitConfig.generate({
// //       model: gemini15Flash,
// //       prompt: `Hello Gemini, my name is ${name}`,
// //     });

//     return json({ response: "response.text" });
//   } catch (error) {
//     console.error('Error generating text:', error);
//     return json({ error: 'Failed to generate response' }, { status: 500 });
//   }
// };

// Client-side component