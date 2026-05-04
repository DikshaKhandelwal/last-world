import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
from routers import game, human, pipeline

app = FastAPI(title='Last Model — System Failure Protocol')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'] if CORS_ORIGINS == ['*'] else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(game.router, prefix='/api/game')
app.include_router(pipeline.router, prefix='/api/pipeline')
app.include_router(human.router, prefix='/api/human')


@app.get('/health')
async def health():
    return {'status': 'operational', 'model': 'qwen3:0.6b', 'mode': 'survival'}
