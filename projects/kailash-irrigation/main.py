"""
冈仁波齐天山灌溉系统 - 主应用

FastAPI + MHP 控制器集成示例
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入 MHP 模块
from src.mhp_client import create_client, MHPAsyncPoller
from src.mhp_client.service import MHPDeviceService
from src.api.routes import mhp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    account = os.getenv("MHP_ACCOUNT", "88888888888")
    registid = os.getenv("MHP_REGISTID", "2119992778")
    poll_interval = int(os.getenv("MHP_POLL_INTERVAL", "30"))
    
    print("🌾 冈仁波齐天山灌溉系统启动中...")
    print(f"   连接 MHP 控制器: {account}")
    
    # 初始化服务
    service = MHPDeviceService(account, registid)
    mhp.init_mhp_service(account, registid)
    
    # 启动后台轮询
    poller = MHPAsyncPoller(service, interval=poll_interval)
    await poller.start()
    
    print("✅ MHP 轮询服务已启动")
    
    yield
    
    # 关闭时清理
    print("🛑 正在关闭服务...")
    await poller.stop()
    service.close()
    print("✅ 服务已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="冈仁波齐天山灌溉系统 API",
    description="智能水肥一体化控制系统 - MHP 控制器对接",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(mhp.router)


@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "冈仁波齐天山灌溉系统",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "mhp_devices": "/mhp/devices",
            "mhp_health": "/mhp/health",
            "mhp_summary": "/mhp/summary"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "kailash-irrigation"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("API_DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
