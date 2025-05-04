// import { genkit } from 'genkit';
// import { googleAI, gemini } from '@genkit-ai/googleai';
// import express from 'express'
// import cors from 'cors';
// import { createClient } from '@supabase/supabase-js'
// import 'dotenv/config'
// const supabaseUrl = process.env.SUPABASE_URL
// const supabaseKey = process.env.SUPABASE_API_KEY;
// const app = express();
// app.use(cors())
// app.use(express.json())
// const supabase = createClient(supabaseUrl, supabaseKey);
// const genkitConfig = genkit({
//     plugins: [googleAI({ apiKey: process.env.GOOGLE_GENAI_API_KEY })],
//     model: gemini('gemini-1.5-flash'),
// });

// app.get('/generate', async (req, res) => {
//     const search = req.query.search;
//     try {
//         const response = await genkitConfig.generate(search)
//         res.status(200).json({
//             message: response.text
//         })
//     } catch (error) {
//         res.status(500).json({
//             message: error.message
//         })

//     }

// })
// app.get('/api/profile', async (req, res) => {
//     try {
//         const response = await supabase.auth.getUser();
//         return  res.status(200).json({
//             user: response.data.user
//         })
//     } catch (error) {
//         res.status(500).json({
//             message: error.message
//         })
//     }
// })
// app.post('/api/auth/signup', async (req, res) => {
//     try {
//         const response = await supabase.auth.signUp({
//             email: req.body.email,
//             password: req.body.password,
//             options: {
//                 data: {
//                     name: req.body.name,
//                     phone: req.body.phone
//                 }
//             }
//         })
//         res.status(200).json({
//             message: "User Signup successfully",
//             user: response.data.user,
//             token: response.data.session
//         });
//     } catch (error) {

//     }
// })

// app.post('/api/auth/signin', async (req, res) => {
//     try {
//         const response = await supabase.auth.signInWithPassword({
//             email: req.body.email,
//             password: req.body.password
//         })
//         console.log(
//             "aaa",
//             response
//         );
        
//         res.status(200).json({
//             message: "User logged In successfully",
//             user: response.data.user,
//             token: response.data.session
//         });
//     } catch (error) {
//         res.status(500).json({
//             message: error.message
//         })
//     }
// })

// app.listen(3001, () => {
//     console.log('server listening on 3001')
// })



import { HfInference } from '@huggingface/inference';
import axios from 'axios';
import { genkit } from 'genkit';
import { googleAI, gemini } from '@genkit-ai/googleai';
import express from 'express'
import cors from 'cors';
import { createClient } from '@supabase/supabase-js'
import 'dotenv/config';
import pkg from 'parquetjs';
const { ParquetReader } = pkg;
const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_API_KEY;
const app = express();
app.use(cors())
app.use(express.json())
const supabase = createClient(supabaseUrl, supabaseKey);
const genkitConfig = genkit({
    plugins: [googleAI({ apiKey: process.env.GOOGLE_GENAI_API_KEY })],
    model: gemini('gemini-1.5-flash'),
});
const hf = new HfInference(process.env.HUGGINGFACE_API_KEY);


app.get('/generate', async (req, res) => {
    const search = req.query.search;
    try {
        const response = await genkitConfig.generate(search)
        res.status(200).json({
            message: response.text
        })
    } catch (error) {
        res.status(500).json({
            message: error.message
        })

    }

})
app.get('/api/profile', async (req, res) => {
    try {
        const response = await supabase.auth.getUser();
        return  res.status(200).json({
            user: response.data.user
        })
    } catch (error) {
        res.status(500).json({
            message: error.message
        })
    }
})
app.post('/api/auth/signup', async (req, res) => {
    try {
        const response = await supabase.auth.signUp({
            email: req.body.email,
            password: req.body.password,
            options: {
                data: {
                    name: req.body.name,
                    phone: req.body.phone
                }
            }
        })
        res.status(200).json({
            message: "User Signup successfully",
            user: response.data.user,
            token: response.data.session
        });
    } catch (error) {

    }
})

app.post('/api/auth/signin', async (req, res) => {
    try {
        const response = await supabase.auth.signInWithPassword({
            email: req.body.email,
            password: req.body.password
        })
        console.log(
            "aaa",
            response.data.session
        );
        
        res.status(200).json({
            message: "User logged In successfully",
            user: response.data.user,
            token: response.data.session
        });
    } catch (error) {
        res.status(500).json({
            message: error.message
        })
    }
})
// Add these new endpoints to your Express app

/**
 * Get a random image pair from the dataset
 */
app.get('/api/image-pair', async (req, res) => {
    try {
        // Load the dataset
        const response = await axios.get(
            'https://huggingface.co/api/datasets/data-is-better-together/image-preferences-results'
        );
        console.log(
            "d",
            response.data
        );
        


        res.status(200).json({
            pair: response.data
        });
    } catch (error) {
        res.status(500).json({
            message: error.message
        });
    }
});


app.get('/api/generate-image', async (req, res) => {
    try {
        // Step 1: Get dataset metadata
        const metadataResponse = await axios.get(
            'https://huggingface.co/api/datasets/data-is-better-together/image-preferences-results'
        );

        // Step 2: Find the Parquet file URL
        const parquetFile = metadataResponse.data.siblings.find((file) =>
            file.rfilename.includes('train-00000-of-00001.parquet')
        );

        if (!parquetFile) {
            throw new Error('Parquet file not found in dataset');
        }

        // Step 3: Construct the Parquet file URL
        const parquetUrl = `https://huggingface.co/datasets/data-is-better-together/image-preferences-results/resolve/main/${parquetFile.rfilename}`;

        // Step 4: Fetch the Parquet file
        const parquetResponse = await axios.get(parquetUrl, {
            responseType: 'arraybuffer',
        });

        // Step 5: Parse the Parquet file
        const buffer = Buffer.from(parquetResponse.data);
        const reader = await ParquetReader.openBuffer(buffer);
        const cursor = reader.getCursor();
        const records = [];
        let record;
        while ((record = await cursor.next())) {
            records.push(record);
        }
        await reader.close();

        // Step 6: Select a random prompt
        const randomRecord = records[Math.floor(Math.random() * records.length)];
        const prompt = randomRecord.prompt; // Assuming 'prompt' is a column in the dataset

        // Step 7: Generate an image using Hugging Face Inference API
        const imageResponse = await axios.post(
            'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2',
            {
                inputs: prompt,
            },
            {
                headers: {
                    Authorization: `Bearer ${HF_API_TOKEN}`,
                    'Content-Type': 'application/json',
                },
                responseType: 'arraybuffer', // For binary image data
            }
        );

        // Step 8: Convert image to base64 for easier handling
        const imageBase64 = Buffer.from(imageResponse.data).toString('base64');

        // Step 9: Return the generated image and prompt
        res.status(200).json({
            prompt: prompt,
            generatedImage: `data:image/png;base64,${imageBase64}`,
            originalPair: randomRecord, // Optionally include the dataset's image pair
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({
            message: error.message,
        });
    }
});
/*
 * Submit a preference for an image pair
 */
app.post('/api/submit-preference', async (req, res) => {
    try {
        const { pairId, preference, userId } = req.body;

        // In a real app, you'd store this in your database
        const { data, error } = await supabase
            .from('user_preferences')
            .insert([
                {
                    pair_id: pairId,
                    preference: preference,
                    user_id: userId,
                    created_at: new Date().toISOString()
                }
            ]);

        if (error) throw error;

        res.status(200).json({
            message: "Preference saved successfully"
        });
    } catch (error) {
        res.status(500).json({
            message: error.message
        });
    }
});

/**
 * Get aggregated preferences for analysis
 */
app.get('/api/preference-stats', async (req, res) => {
    try {
        // Example: Get preference counts from your database
        const { data, error } = await supabase
            .from('user_preferences')
            .select('preference, count(*)')
            .group('preference');

        if (error) throw error;

        res.status(200).json({
            stats: data
        });
    } catch (error) {
        res.status(500).json({
            message: error.message
        });
    }
});

// Helper function to load the dataset (you might want to cache this)
async function loadDataset() {
    try {
        // Note: In Node.js, you might need to use the Hugging Face API
        // or a different approach since the datasets library is Python-based
        const response = await axios.get(
            'https://huggingface.co/datasets/data-is-better-together/image-preferences-results/raw/main/data/train-00000-of-00001.parquet'
        );

        // You would need to parse the Parquet file here
        // For simplicity, we'll return an empty array
        console.log(
            response
        );
        
        return [];
    } catch (error) {
        console.error("Error loading dataset:", error);
        return [];
    }
}


app.listen(3001, () => {
    console.log('server listening on 3001')
})


// from transformers import AutoModelForCausalLM, AutoTokenizer
// import torch

// class QwenChatbot:
//     def __init__(self, model_name="Qwen/Qwen3-235B-A22B"):
//         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
//         self.model = AutoModelForCausalLM.from_pretrained(
//             model_name,
//             torch_dtype="auto",
//             device_map="auto"
//         )
//         self.history = []

//     def generate_response(self, user_input, enable_thinking=True):
//         # Check for /think or /no_think in user input to override enable_thinking
//         if "/no_think" in user_input:
//             enable_thinking = False
//             user_input = user_input.replace("/no_think", "").strip()
//         elif "/think" in user_input:
//             enable_thinking = True
//             user_input = user_input.replace("/think", "").strip()

//         messages = self.history + [{"role": "user", "content": user_input}]

//         text = self.tokenizer.apply_chat_template(
//             messages,
//             tokenize=False,
//             add_generation_prompt=True,
//             enable_thinking=enable_thinking
//         )

//         inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        
//         # Set sampling parameters based on thinking mode
//         generate_kwargs = {
//             "max_new_tokens": 32768,
//             "do_sample": True,
//             "top_k": 20,
//             "min_p": 0.0
//         }
//         if enable_thinking:
//             generate_kwargs.update({"temperature": 0.6, "top_p": 0.95})
//         else:
//             generate_kwargs.update({"temperature": 0.7, "top_p": 0.8})

//         response_ids = self.model.generate(**inputs, **generate_kwargs)[0][len(inputs.input_ids[0]):].tolist()
//         response = self.tokenizer.decode(response_ids, skip_special_tokens=True).strip()

//         # Update history
//         self.history.append({"role": "user", "content": user_input})
//         self.history.append({"role": "assistant", "content": response})

//         return response

// # Example Usage
// if __name__ == "__main__":
//     chatbot = QwenChatbot()

//     # First input (default thinking mode)
//     user_input_1 = "How many r's in strawberries?"
//     print(f"User: {user_input_1}")
//     response_1 = chatbot.generate_response(user_input_1)
//     print(f"Bot: {response_1}")
//     print("----------------------")

//     # Second input with /no_think
//     user_input_2 = "Then, how many r's in blueberries? /no_think"
//     print(f"User: {user_input_2}")
//     response_2 = chatbot.generate_response(user_input_2)
//     print(f"Bot: {response_2}")
//     print("----------------------")

//     # Third input with /think
//     user_input_3 = "Really? /think"
//     print(f"User: {user_input_3}")
//     response_3 = chatbot.generate_response(user_input_3)
//     print(f"Bot: {response_3}")