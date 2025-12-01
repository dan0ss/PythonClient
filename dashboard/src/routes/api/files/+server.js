import { json } from '@sveltejs/kit';
import { readdir, readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const JSON_DIR = join(__dirname, '..', '..', '..', '..', '..', 'outputs', 'json');

export async function GET({ url }) {
	const filename = url.searchParams.get('file');
	
	try {
		if (filename) {
			// Return specific file contents
			const filePath = join(JSON_DIR, filename);
			const content = await readFile(filePath, 'utf-8');
			return json(JSON.parse(content));
		} else {
			// Return list of files
			const files = await readdir(JSON_DIR);
			const jsonFiles = files.filter(f => f.endsWith('.json'));
			return json(jsonFiles);
		}
	} catch (error) {
		console.error('Error:', error);
		return json({ error: error.message }, { status: 500 });
	}
}

