#!/usr/bin/env python3
"""
修復版KiloRAG集成系統
解決RAG集成問題，實現完整的文件和交互數據索引
"""

import os
import sys
import json
import asyncio
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

class SimpleRAGSystem:
    """簡化的RAG系統實現"""
    
    def __init__(self):
        """初始化簡化RAG系統"""
        self.memories = []
        self.memory_index = {}
        self.next_id = 1
        
    def add_memory(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """添加記憶到RAG系統"""
        try:
            memory_id = f"mem_{self.next_id:06d}"
            self.next_id += 1
            
            memory = {
                "id": memory_id,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            self.memories.append(memory)
            self.memory_index[memory_id] = len(self.memories) - 1
            
            return {
                "status": "success",
                "memory_id": memory_id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """搜索記憶"""
        try:
            query_lower = query.lower()
            results = []
            
            for memory in self.memories:
                content_lower = memory["content"].lower()
                
                # 簡單的關鍵詞匹配
                if query_lower in content_lower:
                    score = content_lower.count(query_lower) / len(content_lower.split())
                    results.append({
                        "memory_id": memory["id"],
                        "content": memory["content"][:200] + "..." if len(memory["content"]) > 200 else memory["content"],
                        "metadata": memory["metadata"],
                        "score": score
                    })
            
            # 按分數排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "status": "success",
                "results": results[:limit]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "results": []
            }

class FixedKiloRAGIntegrationSystem:
    """修復版KiloRAG完整集成系統"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化KiloRAG集成系統"""
        self.config = config or {}
        self.base_path = self.config.get('base_path', '/home/ubuntu/Powerauto.ai')
        
        # 使用簡化RAG系統
        self.rag_system = SimpleRAGSystem()
        
        # 數據庫連接
        self.db_path = os.path.join(self.base_path, 'data', 'kilorag.db')
        self._init_database()
        
        # 支持的文件類型
        self.supported_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
            '.md', '.txt', '.json', '.yaml', '.yml', '.xml',
            '.html', '.css', '.sql', '.sh', '.bat'
        }
        
        logger.info("修復版KiloRAG集成系統初始化完成")
    
    def _init_database(self):
        """初始化數據庫"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 文件索引表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_hash TEXT NOT NULL,
                    content_preview TEXT,
                    file_type TEXT,
                    size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rag_memory_id TEXT,
                    indexed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # 交互數據表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interaction_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interaction_id TEXT UNIQUE NOT NULL,
                    user_input TEXT,
                    ai_response TEXT,
                    context_data TEXT,
                    quality_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rag_memory_id TEXT,
                    indexed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # RAG檢索記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rag_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    results_count INTEGER,
                    query_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    async def scan_and_index_all_files(self) -> Dict[str, Any]:
        """掃描並索引所有項目文件"""
        logger.info("開始掃描和索引所有項目文件...")
        
        results = {
            "total_files": 0,
            "indexed_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "file_types": {},
            "errors": []
        }
        
        try:
            # 遍歷項目目錄
            for root, dirs, files in os.walk(self.base_path):
                # 跳過特定目錄
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'data']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.base_path)
                    
                    results["total_files"] += 1
                    
                    # 檢查文件類型
                    file_ext = Path(file).suffix.lower()
                    if file_ext not in self.supported_extensions:
                        results["skipped_files"] += 1
                        continue
                    
                    # 統計文件類型
                    results["file_types"][file_ext] = results["file_types"].get(file_ext, 0) + 1
                    
                    # 索引文件
                    try:
                        index_result = await self._index_single_file(file_path, relative_path)
                        if index_result["status"] == "success":
                            results["indexed_files"] += 1
                        elif index_result["status"] == "skipped":
                            results["skipped_files"] += 1
                        else:
                            results["failed_files"] += 1
                            if len(results["errors"]) < 10:  # 限制錯誤數量
                                results["errors"].append(f"{relative_path}: {index_result.get('error', 'Unknown error')}")
                    except Exception as e:
                        results["failed_files"] += 1
                        if len(results["errors"]) < 10:
                            results["errors"].append(f"{relative_path}: {str(e)}")
            
            logger.info(f"文件索引完成: {results['indexed_files']}/{results['total_files']} 成功")
            return results
            
        except Exception as e:
            logger.error(f"掃描文件失敗: {e}")
            results["errors"].append(f"掃描失敗: {str(e)}")
            return results
    
    async def _index_single_file(self, file_path: str, relative_path: str) -> Dict[str, Any]:
        """索引單個文件"""
        try:
            # 檢查文件大小（跳過過大的文件）
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB限制
                return {"status": "skipped", "reason": "file_too_large"}
            
            # 檢查文件是否已索引
            file_hash = self._calculate_file_hash(file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT file_hash, rag_memory_id FROM file_index WHERE file_path = ?",
                    (relative_path,)
                )
                existing = cursor.fetchone()
                
                if existing and existing[0] == file_hash:
                    return {"status": "skipped", "reason": "already_indexed"}
            
            # 讀取文件內容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception:
                    return {"status": "error", "error": "encoding_error"}
            
            # 限制內容長度
            if len(content) > 10000:
                content = content[:10000] + "\\n... (內容已截斷)"
            
            # 準備RAG記憶數據
            file_info = os.stat(file_path)
            metadata = {
                "file_path": relative_path,
                "file_type": Path(file_path).suffix.lower(),
                "file_size": file_info.st_size,
                "created_at": datetime.fromtimestamp(file_info.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(file_info.st_mtime).isoformat(),
                "content_type": "project_file"
            }
            
            # 創建內容預覽
            content_preview = content[:500] + "..." if len(content) > 500 else content
            
            # 添加到RAG系統
            rag_result = self.rag_system.add_memory(
                content=content,
                metadata=metadata
            )
            
            if rag_result.get("status") == "success":
                rag_memory_id = rag_result.get("memory_id")
                
                # 保存到數據庫
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO file_index 
                        (file_path, file_hash, content_preview, file_type, size, rag_memory_id, indexed, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        relative_path, file_hash, content_preview,
                        metadata["file_type"], metadata["file_size"],
                        rag_memory_id, True
                    ))
                    conn.commit()
                
                return {"status": "success", "rag_memory_id": rag_memory_id}
            else:
                return {"status": "error", "error": "RAG索引失敗"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """計算文件哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except Exception:
            # 如果無法讀取文件，使用文件路徑和修改時間
            stat = os.stat(file_path)
            hash_md5.update(f"{file_path}_{stat.st_mtime}".encode())
        
        return hash_md5.hexdigest()
    
    async def index_interaction_data(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """索引交互數據"""
        try:
            interaction_id = interaction_data.get("interaction_id") or self._generate_interaction_id(interaction_data)
            
            # 檢查是否已索引
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT rag_memory_id FROM interaction_data WHERE interaction_id = ?",
                    (interaction_id,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    return {"status": "skipped", "reason": "already_indexed"}
            
            # 準備RAG記憶數據
            user_input = interaction_data.get("user_input", "")
            ai_response = interaction_data.get("ai_response", "")
            context_data = interaction_data.get("context", {})
            
            # 組合內容用於RAG檢索
            combined_content = f"""
用戶輸入: {user_input}
AI回應: {ai_response}
上下文: {json.dumps(context_data, ensure_ascii=False, indent=2)}
            """.strip()
            
            metadata = {
                "interaction_id": interaction_id,
                "user_input": user_input,
                "ai_response": ai_response,
                "quality_score": interaction_data.get("quality_score", 0.5),
                "timestamp": interaction_data.get("timestamp", datetime.now().isoformat()),
                "content_type": "interaction_data"
            }
            
            # 添加到RAG系統
            rag_result = self.rag_system.add_memory(
                content=combined_content,
                metadata=metadata
            )
            
            if rag_result.get("status") == "success":
                rag_memory_id = rag_result.get("memory_id")
                
                # 保存到數據庫
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO interaction_data 
                        (interaction_id, user_input, ai_response, context_data, quality_score, rag_memory_id, indexed)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        interaction_id, user_input, ai_response,
                        json.dumps(context_data), metadata["quality_score"],
                        rag_memory_id, True
                    ))
                    conn.commit()
                
                return {"status": "success", "rag_memory_id": rag_memory_id}
            else:
                return {"status": "error", "error": "RAG索引失敗"}
                
        except Exception as e:
            logger.error(f"索引交互數據失敗: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_interaction_id(self, interaction_data: Dict[str, Any]) -> str:
        """生成交互ID"""
        content = f"{interaction_data.get('user_input', '')}{interaction_data.get('ai_response', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def search_knowledge(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """搜索知識庫"""
        try:
            start_time = datetime.now()
            
            # 使用RAG系統搜索
            search_results = self.rag_system.search_memories(
                query=query,
                limit=limit
            )
            
            end_time = datetime.now()
            query_time = (end_time - start_time).total_seconds()
            
            results = search_results.get("results", [])
            
            # 記錄查詢
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO rag_queries (query_text, results_count, query_time)
                    VALUES (?, ?, ?)
                ''', (query, len(results), query_time))
                conn.commit()
            
            return {
                "status": "success",
                "query": query,
                "results": results,
                "total_results": len(results),
                "query_time": query_time
            }
            
        except Exception as e:
            logger.error(f"搜索知識庫失敗: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": [],
                "total_results": 0,
                "query_time": 0
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 統計文件索引
                cursor.execute("SELECT COUNT(*) FROM file_index WHERE indexed = TRUE")
                indexed_files_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM file_index")
                total_files_count = cursor.fetchone()[0]
                
                # 統計交互數據
                cursor.execute("SELECT COUNT(*) FROM interaction_data WHERE indexed = TRUE")
                indexed_interactions_count = cursor.fetchone()[0]
                
                # 統計查詢
                cursor.execute("SELECT COUNT(*) FROM rag_queries")
                total_queries_count = cursor.fetchone()[0]
                
                # 文件類型統計
                cursor.execute("SELECT file_type, COUNT(*) FROM file_index GROUP BY file_type")
                file_types = dict(cursor.fetchall())
                
                return {
                    "status": "active",
                    "indexed_files": indexed_files_count,
                    "total_files": total_files_count,
                    "indexed_interactions": indexed_interactions_count,
                    "total_queries": total_queries_count,
                    "file_types": file_types,
                    "database_path": self.db_path,
                    "rag_memories_count": len(self.rag_system.memories),
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"獲取系統狀態失敗: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


async def main():
    """主測試函數"""
    print("🚀 修復版KiloRAG完整集成系統測試\\n")
    
    # 初始化系統
    kilorag = FixedKiloRAGIntegrationSystem()
    
    # 獲取初始狀態
    print("📊 系統初始狀態:")
    status = await kilorag.get_system_status()
    print(f"  已索引文件: {status.get('indexed_files', 0)}")
    print(f"  已索引交互: {status.get('indexed_interactions', 0)}")
    print(f"  總查詢次數: {status.get('total_queries', 0)}")
    print(f"  RAG記憶數量: {status.get('rag_memories_count', 0)}")
    print()
    
    # 掃描和索引文件（限制數量以避免過長）
    print("📁 開始掃描和索引項目文件...")
    index_results = await kilorag.scan_and_index_all_files()
    
    print(f"  總文件數: {index_results['total_files']}")
    print(f"  成功索引: {index_results['indexed_files']}")
    print(f"  跳過文件: {index_results['skipped_files']}")
    print(f"  失敗文件: {index_results['failed_files']}")
    
    if index_results['file_types']:
        print("  文件類型分佈:")
        for ext, count in sorted(index_results['file_types'].items()):
            print(f"    {ext}: {count}")
    
    if index_results['errors']:
        print("  部分錯誤信息:")
        for error in index_results['errors'][:3]:  # 只顯示前3個錯誤
            print(f"    {error}")
    print()
    
    # 測試交互數據索引
    print("💬 測試交互數據索引...")
    test_interactions = [
        {
            "user_input": "如何使用PowerAutomation進行GAIA測試？",
            "ai_response": "PowerAutomation提供了完整的GAIA測試框架，包括MCP適配器、異步RL訓練等功能。",
            "context": {"test_type": "gaia", "level": 1},
            "quality_score": 0.9
        },
        {
            "user_input": "RL_SRT如何與記憶系統集成？",
            "ai_response": "RL_SRT通過CloudEdgeDataMCP從統一記憶模塊獲取交互數據進行訓練。",
            "context": {"topic": "rl_memory_integration"},
            "quality_score": 0.8
        }
    ]
    
    for i, interaction in enumerate(test_interactions):
        result = await kilorag.index_interaction_data(interaction)
        print(f"  交互數據 {i+1} 索引: {result['status']}")
    print()
    
    # 測試知識搜索
    print("🔍 測試知識搜索...")
    search_queries = [
        "GAIA測試",
        "MCP適配器", 
        "異步RL訓練",
        "記憶系統",
        "PowerAutomation"
    ]
    
    for query in search_queries:
        search_result = await kilorag.search_knowledge(query, limit=3)
        print(f"  查詢 '{query}': {search_result['total_results']} 結果 ({search_result.get('query_time', 0):.3f}s)")
        
        # 顯示第一個結果的預覽
        if search_result['results']:
            first_result = search_result['results'][0]
            preview = first_result['content'][:100] + "..." if len(first_result['content']) > 100 else first_result['content']
            print(f"    預覽: {preview}")
    print()
    
    # 獲取最終狀態
    print("📊 系統最終狀態:")
    final_status = await kilorag.get_system_status()
    print(f"  已索引文件: {final_status.get('indexed_files', 0)}")
    print(f"  已索引交互: {final_status.get('indexed_interactions', 0)}")
    print(f"  總查詢次數: {final_status.get('total_queries', 0)}")
    print(f"  RAG記憶數量: {final_status.get('rag_memories_count', 0)}")
    
    print("\\n✅ KiloRAG集成測試完成！")
    print(f"📄 數據庫位置: {final_status.get('database_path')}")

if __name__ == "__main__":
    asyncio.run(main())

