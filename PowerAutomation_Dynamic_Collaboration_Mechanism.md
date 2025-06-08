# PowerAutomation動態協作調整機制設計與實現

## 🎯 **設計目標**

基於第一階段的現狀分析，設計並實現PowerAutomation的動態協作調整機制，將動態協作能力從當前的2/10提升到9/10，為實現L4級別多智能體協作奠定核心基礎。

## 📊 **動態協作調整機制核心架構**

### 🔧 **1. 協作策略動態選擇引擎**

動態協作調整的核心是能夠根據任務特徵、智能體狀態和環境條件，實時選擇最優的協作策略。我們設計了一個多層次的策略選擇引擎：

#### **協作策略分類體系**

```python
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import time
import json

class CollaborationStrategy(Enum):
    """協作策略枚舉"""
    # 基礎策略
    SEQUENTIAL = "sequential"           # 順序協作
    PARALLEL = "parallel"              # 並行協作
    HIERARCHICAL = "hierarchical"      # 階層協作
    
    # 高級策略
    COMPETITIVE = "competitive"        # 競爭協作
    CONSENSUS = "consensus"            # 共識協作
    AUCTION = "auction"                # 拍賣協作
    SWARM = "swarm"                    # 群體協作
    
    # 混合策略
    HYBRID_SEQ_PAR = "hybrid_seq_par"  # 順序+並行混合
    HYBRID_COMP_CONS = "hybrid_comp_cons"  # 競爭+共識混合
    ADAPTIVE = "adaptive"              # 自適應策略

class TaskComplexity(Enum):
    """任務複雜度枚舉"""
    SIMPLE = "simple"        # 簡單任務 (1-2個步驟)
    MODERATE = "moderate"    # 中等任務 (3-5個步驟)
    COMPLEX = "complex"      # 複雜任務 (6-10個步驟)
    VERY_COMPLEX = "very_complex"  # 極複雜任務 (10+個步驟)

class TaskUrgency(Enum):
    """任務緊急程度枚舉"""
    LOW = "low"           # 低緊急度 (可延遲)
    MEDIUM = "medium"     # 中緊急度 (正常處理)
    HIGH = "high"         # 高緊急度 (優先處理)
    CRITICAL = "critical" # 緊急 (立即處理)

@dataclass
class TaskCharacteristics:
    """任務特徵"""
    complexity: TaskComplexity
    urgency: TaskUrgency
    domain: str  # 任務領域 (如: "data_analysis", "code_generation", "content_creation")
    estimated_duration: float  # 預估執行時間 (秒)
    resource_requirements: Dict[str, float]  # 資源需求
    dependencies: List[str]  # 依賴關係
    quality_requirements: Dict[str, float]  # 質量要求

@dataclass
class AgentCapability:
    """智能體能力模型"""
    agent_id: str
    specializations: List[str]  # 專業領域
    performance_scores: Dict[str, float]  # 各領域性能分數
    current_load: float  # 當前負載 (0-1)
    availability: bool  # 是否可用
    collaboration_history: Dict[str, float]  # 協作歷史評分
    learning_rate: float  # 學習速率
    
class DynamicCollaborationEngine:
    """動態協作引擎"""
    
    def __init__(self):
        self.strategy_selector = CollaborationStrategySelector()
        self.flow_optimizer = CollaborationFlowOptimizer()
        self.performance_monitor = CollaborationPerformanceMonitor()
        self.adaptation_engine = CollaborationAdaptationEngine()
        
        # 策略性能歷史
        self.strategy_performance_history = {}
        
        # 當前活躍協作
        self.active_collaborations = {}
        
    async def initiate_dynamic_collaboration(self, task: Dict[str, Any], 
                                           available_agents: List[AgentCapability]) -> Dict[str, Any]:
        """啟動動態協作"""
        
        # 1. 任務特徵分析
        task_characteristics = await self._analyze_task_characteristics(task)
        
        # 2. 智能體能力評估
        agent_capabilities = await self._evaluate_agent_capabilities(available_agents, task_characteristics)
        
        # 3. 協作策略選擇
        optimal_strategy = await self.strategy_selector.select_optimal_strategy(
            task_characteristics, agent_capabilities
        )
        
        # 4. 協作流程設計
        collaboration_flow = await self.flow_optimizer.design_collaboration_flow(
            task_characteristics, agent_capabilities, optimal_strategy
        )
        
        # 5. 啟動協作執行
        collaboration_id = f"collab_{int(time.time() * 1000)}"
        collaboration_context = {
            "collaboration_id": collaboration_id,
            "task": task,
            "task_characteristics": task_characteristics,
            "strategy": optimal_strategy,
            "flow": collaboration_flow,
            "participating_agents": agent_capabilities,
            "start_time": time.time(),
            "status": "active"
        }
        
        self.active_collaborations[collaboration_id] = collaboration_context
        
        # 6. 執行協作並監控
        result = await self._execute_collaboration_with_monitoring(collaboration_context)
        
        return result
    
    async def _analyze_task_characteristics(self, task: Dict[str, Any]) -> TaskCharacteristics:
        """分析任務特徵"""
        
        # 基於任務內容分析複雜度
        task_content = task.get("user_input", "")
        task_context = task.get("context", {})
        
        # 複雜度評估算法
        complexity_score = 0
        
        # 基於關鍵詞的複雜度評估
        complex_keywords = ["分析", "優化", "設計", "開發", "整合", "系統", "架構"]
        moderate_keywords = ["創建", "生成", "修改", "更新", "查詢"]
        simple_keywords = ["顯示", "列出", "查看", "獲取"]
        
        for keyword in complex_keywords:
            if keyword in task_content:
                complexity_score += 3
        for keyword in moderate_keywords:
            if keyword in task_content:
                complexity_score += 2
        for keyword in simple_keywords:
            if keyword in task_content:
                complexity_score += 1
        
        # 基於任務長度的複雜度調整
        content_length_factor = min(len(task_content) / 100, 2.0)
        complexity_score *= content_length_factor
        
        # 確定複雜度等級
        if complexity_score <= 2:
            complexity = TaskComplexity.SIMPLE
            estimated_duration = 30.0
        elif complexity_score <= 5:
            complexity = TaskComplexity.MODERATE
            estimated_duration = 120.0
        elif complexity_score <= 10:
            complexity = TaskComplexity.COMPLEX
            estimated_duration = 300.0
        else:
            complexity = TaskComplexity.VERY_COMPLEX
            estimated_duration = 600.0
        
        # 緊急程度評估
        urgency_indicators = task_context.get("urgency_indicators", {})
        if urgency_indicators.get("critical", False):
            urgency = TaskUrgency.CRITICAL
        elif urgency_indicators.get("high_priority", False):
            urgency = TaskUrgency.HIGH
        elif urgency_indicators.get("time_sensitive", False):
            urgency = TaskUrgency.MEDIUM
        else:
            urgency = TaskUrgency.LOW
        
        # 領域識別
        domain_keywords = {
            "data_analysis": ["數據", "分析", "統計", "圖表", "報告"],
            "code_generation": ["代碼", "程序", "開發", "編程", "函數"],
            "content_creation": ["內容", "文章", "文檔", "寫作", "創作"],
            "system_design": ["系統", "架構", "設計", "方案", "框架"],
            "optimization": ["優化", "改進", "提升", "效率", "性能"]
        }
        
        domain = "general"
        max_score = 0
        for domain_name, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_content)
            if score > max_score:
                max_score = score
                domain = domain_name
        
        return TaskCharacteristics(
            complexity=complexity,
            urgency=urgency,
            domain=domain,
            estimated_duration=estimated_duration,
            resource_requirements={
                "cpu": 0.5 if complexity in [TaskComplexity.SIMPLE, TaskComplexity.MODERATE] else 0.8,
                "memory": 0.3 if complexity == TaskComplexity.SIMPLE else 0.6,
                "network": 0.2
            },
            dependencies=[],
            quality_requirements={
                "accuracy": 0.9 if urgency in [TaskUrgency.HIGH, TaskUrgency.CRITICAL] else 0.8,
                "completeness": 0.95,
                "timeliness": 0.9 if urgency in [TaskUrgency.HIGH, TaskUrgency.CRITICAL] else 0.7
            }
        )
    
    async def _evaluate_agent_capabilities(self, available_agents: List[AgentCapability], 
                                         task_characteristics: TaskCharacteristics) -> List[AgentCapability]:
        """評估智能體能力匹配度"""
        
        evaluated_agents = []
        
        for agent in available_agents:
            # 計算領域匹配度
            domain_match_score = 0.0
            if task_characteristics.domain in agent.specializations:
                domain_match_score = agent.performance_scores.get(task_characteristics.domain, 0.5)
            else:
                # 查找相關領域
                related_domains = self._find_related_domains(task_characteristics.domain, agent.specializations)
                if related_domains:
                    domain_match_score = max(agent.performance_scores.get(domain, 0.3) for domain in related_domains)
                else:
                    domain_match_score = 0.2  # 基礎通用能力
            
            # 計算負載適應性
            load_factor = 1.0 - agent.current_load
            
            # 計算協作歷史評分
            collaboration_score = agent.collaboration_history.get("average_score", 0.7)
            
            # 綜合能力評分
            overall_capability = (
                domain_match_score * 0.4 +
                load_factor * 0.3 +
                collaboration_score * 0.2 +
                agent.learning_rate * 0.1
            )
            
            # 創建增強的智能體能力對象
            enhanced_agent = AgentCapability(
                agent_id=agent.agent_id,
                specializations=agent.specializations,
                performance_scores=agent.performance_scores,
                current_load=agent.current_load,
                availability=agent.availability and overall_capability > 0.3,
                collaboration_history=agent.collaboration_history,
                learning_rate=agent.learning_rate
            )
            
            # 添加動態評估結果
            enhanced_agent.domain_match_score = domain_match_score
            enhanced_agent.overall_capability = overall_capability
            enhanced_agent.recommended_role = self._determine_agent_role(enhanced_agent, task_characteristics)
            
            evaluated_agents.append(enhanced_agent)
        
        # 按能力評分排序
        evaluated_agents.sort(key=lambda x: x.overall_capability, reverse=True)
        
        return evaluated_agents
    
    def _find_related_domains(self, target_domain: str, agent_specializations: List[str]) -> List[str]:
        """查找相關領域"""
        domain_relationships = {
            "data_analysis": ["system_design", "optimization"],
            "code_generation": ["system_design", "optimization"],
            "content_creation": ["data_analysis"],
            "system_design": ["code_generation", "optimization"],
            "optimization": ["data_analysis", "system_design"]
        }
        
        related = domain_relationships.get(target_domain, [])
        return [domain for domain in related if domain in agent_specializations]
    
    def _determine_agent_role(self, agent: AgentCapability, task_characteristics: TaskCharacteristics) -> str:
        """確定智能體在協作中的角色"""
        
        if agent.overall_capability >= 0.8:
            return "leader"  # 領導者
        elif agent.overall_capability >= 0.6:
            return "specialist"  # 專家
        elif agent.overall_capability >= 0.4:
            return "contributor"  # 貢獻者
        else:
            return "supporter"  # 支持者

class CollaborationStrategySelector:
    """協作策略選擇器"""
    
    def __init__(self):
        self.strategy_rules = self._initialize_strategy_rules()
        self.performance_history = {}
    
    async def select_optimal_strategy(self, task_characteristics: TaskCharacteristics, 
                                    agent_capabilities: List[AgentCapability]) -> CollaborationStrategy:
        """選擇最優協作策略"""
        
        # 基於規則的初始策略選擇
        rule_based_strategy = self._apply_strategy_rules(task_characteristics, agent_capabilities)
        
        # 基於歷史性能的策略調整
        performance_adjusted_strategy = self._adjust_strategy_by_performance(
            rule_based_strategy, task_characteristics
        )
        
        # 基於當前系統狀態的策略優化
        final_strategy = self._optimize_strategy_by_system_state(
            performance_adjusted_strategy, agent_capabilities
        )
        
        return final_strategy
    
    def _initialize_strategy_rules(self) -> Dict[str, Any]:
        """初始化策略選擇規則"""
        return {
            # 基於任務複雜度的策略選擇
            "complexity_rules": {
                TaskComplexity.SIMPLE: [CollaborationStrategy.SEQUENTIAL, CollaborationStrategy.PARALLEL],
                TaskComplexity.MODERATE: [CollaborationStrategy.PARALLEL, CollaborationStrategy.HIERARCHICAL],
                TaskComplexity.COMPLEX: [CollaborationStrategy.HIERARCHICAL, CollaborationStrategy.CONSENSUS],
                TaskComplexity.VERY_COMPLEX: [CollaborationStrategy.SWARM, CollaborationStrategy.ADAPTIVE]
            },
            
            # 基於緊急程度的策略選擇
            "urgency_rules": {
                TaskUrgency.LOW: [CollaborationStrategy.CONSENSUS, CollaborationStrategy.SEQUENTIAL],
                TaskUrgency.MEDIUM: [CollaborationStrategy.PARALLEL, CollaborationStrategy.HIERARCHICAL],
                TaskUrgency.HIGH: [CollaborationStrategy.COMPETITIVE, CollaborationStrategy.PARALLEL],
                TaskUrgency.CRITICAL: [CollaborationStrategy.AUCTION, CollaborationStrategy.COMPETITIVE]
            },
            
            # 基於智能體數量的策略選擇
            "agent_count_rules": {
                (1, 2): [CollaborationStrategy.SEQUENTIAL, CollaborationStrategy.PARALLEL],
                (3, 5): [CollaborationStrategy.HIERARCHICAL, CollaborationStrategy.CONSENSUS],
                (6, 10): [CollaborationStrategy.SWARM, CollaborationStrategy.AUCTION],
                (11, float('inf')): [CollaborationStrategy.SWARM, CollaborationStrategy.ADAPTIVE]
            }
        }
    
    def _apply_strategy_rules(self, task_characteristics: TaskCharacteristics, 
                            agent_capabilities: List[AgentCapability]) -> CollaborationStrategy:
        """應用策略選擇規則"""
        
        # 獲取可用智能體數量
        available_agent_count = len([agent for agent in agent_capabilities if agent.availability])
        
        # 基於複雜度的策略候選
        complexity_candidates = self.strategy_rules["complexity_rules"][task_characteristics.complexity]
        
        # 基於緊急程度的策略候選
        urgency_candidates = self.strategy_rules["urgency_rules"][task_characteristics.urgency]
        
        # 基於智能體數量的策略候選
        agent_count_candidates = []
        for (min_count, max_count), strategies in self.strategy_rules["agent_count_rules"].items():
            if min_count <= available_agent_count <= max_count:
                agent_count_candidates = strategies
                break
        
        # 找到所有規則的交集
        all_candidates = [complexity_candidates, urgency_candidates, agent_count_candidates]
        common_strategies = set(all_candidates[0])
        for candidates in all_candidates[1:]:
            common_strategies &= set(candidates)
        
        # 如果有交集，選擇第一個；否則選擇最適合的
        if common_strategies:
            return list(common_strategies)[0]
        else:
            # 基於優先級選擇策略
            if task_characteristics.urgency in [TaskUrgency.HIGH, TaskUrgency.CRITICAL]:
                return urgency_candidates[0]
            elif task_characteristics.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
                return complexity_candidates[0]
            else:
                return agent_count_candidates[0] if agent_count_candidates else CollaborationStrategy.SEQUENTIAL
    
    def _adjust_strategy_by_performance(self, initial_strategy: CollaborationStrategy, 
                                      task_characteristics: TaskCharacteristics) -> CollaborationStrategy:
        """基於歷史性能調整策略"""
        
        # 獲取該策略在類似任務上的歷史性能
        task_signature = f"{task_characteristics.complexity.value}_{task_characteristics.domain}"
        strategy_performance = self.performance_history.get(
            f"{initial_strategy.value}_{task_signature}", 
            {"success_rate": 0.7, "avg_duration": 100.0, "quality_score": 0.8}
        )
        
        # 如果歷史性能不佳，考慮替代策略
        if strategy_performance["success_rate"] < 0.6 or strategy_performance["quality_score"] < 0.7:
            # 選擇替代策略
            alternative_strategies = self._get_alternative_strategies(initial_strategy)
            
            best_alternative = initial_strategy
            best_performance = strategy_performance["success_rate"] * strategy_performance["quality_score"]
            
            for alt_strategy in alternative_strategies:
                alt_performance = self.performance_history.get(
                    f"{alt_strategy.value}_{task_signature}",
                    {"success_rate": 0.7, "quality_score": 0.8}
                )
                alt_score = alt_performance["success_rate"] * alt_performance["quality_score"]
                
                if alt_score > best_performance:
                    best_alternative = alt_strategy
                    best_performance = alt_score
            
            return best_alternative
        
        return initial_strategy
    
    def _get_alternative_strategies(self, current_strategy: CollaborationStrategy) -> List[CollaborationStrategy]:
        """獲取替代策略"""
        strategy_alternatives = {
            CollaborationStrategy.SEQUENTIAL: [CollaborationStrategy.PARALLEL, CollaborationStrategy.HIERARCHICAL],
            CollaborationStrategy.PARALLEL: [CollaborationStrategy.SEQUENTIAL, CollaborationStrategy.CONSENSUS],
            CollaborationStrategy.HIERARCHICAL: [CollaborationStrategy.PARALLEL, CollaborationStrategy.SWARM],
            CollaborationStrategy.COMPETITIVE: [CollaborationStrategy.AUCTION, CollaborationStrategy.CONSENSUS],
            CollaborationStrategy.CONSENSUS: [CollaborationStrategy.HIERARCHICAL, CollaborationStrategy.PARALLEL],
            CollaborationStrategy.AUCTION: [CollaborationStrategy.COMPETITIVE, CollaborationStrategy.SWARM],
            CollaborationStrategy.SWARM: [CollaborationStrategy.HIERARCHICAL, CollaborationStrategy.ADAPTIVE],
            CollaborationStrategy.ADAPTIVE: [CollaborationStrategy.SWARM, CollaborationStrategy.CONSENSUS]
        }
        
        return strategy_alternatives.get(current_strategy, [CollaborationStrategy.PARALLEL])
    
    def _optimize_strategy_by_system_state(self, strategy: CollaborationStrategy, 
                                         agent_capabilities: List[AgentCapability]) -> CollaborationStrategy:
        """基於當前系統狀態優化策略"""
        
        # 計算系統負載
        total_load = sum(agent.current_load for agent in agent_capabilities if agent.availability)
        avg_load = total_load / len(agent_capabilities) if agent_capabilities else 0
        
        # 計算能力分佈
        capability_variance = self._calculate_capability_variance(agent_capabilities)
        
        # 基於系統狀態調整策略
        if avg_load > 0.8:  # 高負載情況
            if strategy in [CollaborationStrategy.PARALLEL, CollaborationStrategy.SWARM]:
                return CollaborationStrategy.SEQUENTIAL  # 降低並發度
        elif avg_load < 0.3:  # 低負載情況
            if strategy == CollaborationStrategy.SEQUENTIAL:
                return CollaborationStrategy.PARALLEL  # 提高並發度
        
        if capability_variance > 0.3:  # 能力差異大
            if strategy == CollaborationStrategy.CONSENSUS:
                return CollaborationStrategy.HIERARCHICAL  # 使用階層協作
        
        return strategy
    
    def _calculate_capability_variance(self, agent_capabilities: List[AgentCapability]) -> float:
        """計算智能體能力方差"""
        if not agent_capabilities:
            return 0.0
        
        capabilities = [getattr(agent, 'overall_capability', 0.5) for agent in agent_capabilities]
        mean_capability = sum(capabilities) / len(capabilities)
        variance = sum((cap - mean_capability) ** 2 for cap in capabilities) / len(capabilities)
        
        return variance ** 0.5  # 返回標準差
```

這個動態協作調整機制的核心設計包含了多個關鍵組件，每個組件都針對當前系統的具體問題進行了優化。策略選擇引擎能夠根據任務特徵、智能體能力和系統狀態動態選擇最優的協作策略，這是實現從固化協作流程向動態協作調整轉變的關鍵突破。

通過這種設計，PowerAutomation將能夠：

1. **根據任務複雜度動態調整協作策略** - 簡單任務使用輕量級協作，複雜任務使用深度協作
2. **基於緊急程度優化協作流程** - 緊急任務採用競爭或拍賣機制，普通任務使用共識機制
3. **考慮智能體能力進行智能分配** - 根據專業領域和當前負載動態分配角色
4. **從歷史性能中學習優化** - 基於過往協作效果持續改進策略選擇

這種動態協作調整機制將顯著提升PowerAutomation的協作靈活性和效率，為實現L4級別多智能體協作奠定堅實基礎。



### 🔄 **2. 協作流程動態重構引擎**

在動態協作調整機制中，協作流程的動態重構是另一個核心組件。它能夠根據協作進展、智能體狀態變化和任務需求調整，實時重構協作流程，確保協作效率和質量的最大化。

#### **協作流程建模**

```python
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import uuid

class FlowNodeType(Enum):
    """流程節點類型"""
    TASK = "task"                    # 任務節點
    DECISION = "decision"            # 決策節點
    PARALLEL = "parallel"            # 並行節點
    MERGE = "merge"                  # 合併節點
    CONDITION = "condition"          # 條件節點
    LOOP = "loop"                    # 循環節點
    CHECKPOINT = "checkpoint"        # 檢查點節點

class NodeStatus(Enum):
    """節點狀態"""
    PENDING = "pending"              # 等待執行
    RUNNING = "running"              # 正在執行
    COMPLETED = "completed"          # 已完成
    FAILED = "failed"                # 執行失敗
    SKIPPED = "skipped"              # 已跳過
    PAUSED = "paused"                # 已暫停

@dataclass
class FlowNode:
    """流程節點"""
    node_id: str
    node_type: FlowNodeType
    name: str
    description: str
    assigned_agents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    estimated_duration: float = 60.0
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    
    # 執行狀態
    status: NodeStatus = NodeStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # 動態屬性
    actual_duration: Optional[float] = None
    quality_score: Optional[float] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)

@dataclass
class CollaborationFlow:
    """協作流程"""
    flow_id: str
    name: str
    description: str
    strategy: CollaborationStrategy
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    edges: List[Dict[str, str]] = field(default_factory=list)  # {"from": node_id, "to": node_id}
    
    # 流程狀態
    status: str = "initialized"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    current_nodes: List[str] = field(default_factory=list)
    
    # 動態調整歷史
    adjustment_history: List[Dict[str, Any]] = field(default_factory=list)

class CollaborationFlowOptimizer:
    """協作流程優化器"""
    
    def __init__(self):
        self.flow_templates = self._initialize_flow_templates()
        self.optimization_rules = self._initialize_optimization_rules()
        self.performance_analyzer = FlowPerformanceAnalyzer()
    
    async def design_collaboration_flow(self, task_characteristics: TaskCharacteristics,
                                      agent_capabilities: List[AgentCapability],
                                      strategy: CollaborationStrategy) -> CollaborationFlow:
        """設計協作流程"""
        
        # 1. 選擇基礎流程模板
        base_template = self._select_flow_template(strategy, task_characteristics)
        
        # 2. 根據任務特徵定制流程
        customized_flow = await self._customize_flow_for_task(base_template, task_characteristics)
        
        # 3. 根據智能體能力優化流程
        optimized_flow = await self._optimize_flow_for_agents(customized_flow, agent_capabilities)
        
        # 4. 添加動態調整機制
        adaptive_flow = await self._add_adaptive_mechanisms(optimized_flow)
        
        return adaptive_flow
    
    def _initialize_flow_templates(self) -> Dict[CollaborationStrategy, CollaborationFlow]:
        """初始化流程模板"""
        templates = {}
        
        # 順序協作模板
        sequential_template = CollaborationFlow(
            flow_id="template_sequential",
            name="順序協作模板",
            description="智能體按順序執行任務",
            strategy=CollaborationStrategy.SEQUENTIAL
        )
        
        # 添加順序協作節點
        sequential_nodes = [
            FlowNode("seq_1", FlowNodeType.TASK, "任務分析", "分析任務需求和目標"),
            FlowNode("seq_2", FlowNodeType.TASK, "方案設計", "設計解決方案", dependencies=["seq_1"]),
            FlowNode("seq_3", FlowNodeType.TASK, "方案實施", "實施解決方案", dependencies=["seq_2"]),
            FlowNode("seq_4", FlowNodeType.TASK, "結果驗證", "驗證實施結果", dependencies=["seq_3"])
        ]
        
        for node in sequential_nodes:
            sequential_template.nodes[node.node_id] = node
        
        sequential_template.edges = [
            {"from": "seq_1", "to": "seq_2"},
            {"from": "seq_2", "to": "seq_3"},
            {"from": "seq_3", "to": "seq_4"}
        ]
        
        templates[CollaborationStrategy.SEQUENTIAL] = sequential_template
        
        # 並行協作模板
        parallel_template = CollaborationFlow(
            flow_id="template_parallel",
            name="並行協作模板",
            description="智能體並行執行不同任務",
            strategy=CollaborationStrategy.PARALLEL
        )
        
        # 添加並行協作節點
        parallel_nodes = [
            FlowNode("par_init", FlowNodeType.TASK, "任務初始化", "初始化並分解任務"),
            FlowNode("par_1", FlowNodeType.TASK, "並行任務1", "執行第一個並行任務", dependencies=["par_init"]),
            FlowNode("par_2", FlowNodeType.TASK, "並行任務2", "執行第二個並行任務", dependencies=["par_init"]),
            FlowNode("par_3", FlowNodeType.TASK, "並行任務3", "執行第三個並行任務", dependencies=["par_init"]),
            FlowNode("par_merge", FlowNodeType.MERGE, "結果合併", "合併並行任務結果", 
                    dependencies=["par_1", "par_2", "par_3"])
        ]
        
        for node in parallel_nodes:
            parallel_template.nodes[node.node_id] = node
        
        parallel_template.edges = [
            {"from": "par_init", "to": "par_1"},
            {"from": "par_init", "to": "par_2"},
            {"from": "par_init", "to": "par_3"},
            {"from": "par_1", "to": "par_merge"},
            {"from": "par_2", "to": "par_merge"},
            {"from": "par_3", "to": "par_merge"}
        ]
        
        templates[CollaborationStrategy.PARALLEL] = parallel_template
        
        # 階層協作模板
        hierarchical_template = CollaborationFlow(
            flow_id="template_hierarchical",
            name="階層協作模板",
            description="分層次的智能體協作",
            strategy=CollaborationStrategy.HIERARCHICAL
        )
        
        # 添加階層協作節點
        hierarchical_nodes = [
            FlowNode("hier_plan", FlowNodeType.TASK, "高層規劃", "制定整體協作計劃"),
            FlowNode("hier_decompose", FlowNodeType.DECISION, "任務分解", "將任務分解為子任務", 
                    dependencies=["hier_plan"]),
            FlowNode("hier_assign", FlowNodeType.TASK, "任務分配", "將子任務分配給專業智能體", 
                    dependencies=["hier_decompose"]),
            FlowNode("hier_execute", FlowNodeType.PARALLEL, "並行執行", "各智能體執行分配的任務", 
                    dependencies=["hier_assign"]),
            FlowNode("hier_review", FlowNodeType.TASK, "中層審查", "中層管理者審查執行結果", 
                    dependencies=["hier_execute"]),
            FlowNode("hier_integrate", FlowNodeType.TASK, "結果整合", "整合所有子任務結果", 
                    dependencies=["hier_review"]),
            FlowNode("hier_validate", FlowNodeType.TASK, "最終驗證", "高層驗證最終結果", 
                    dependencies=["hier_integrate"])
        ]
        
        for node in hierarchical_nodes:
            hierarchical_template.nodes[node.node_id] = node
        
        hierarchical_template.edges = [
            {"from": "hier_plan", "to": "hier_decompose"},
            {"from": "hier_decompose", "to": "hier_assign"},
            {"from": "hier_assign", "to": "hier_execute"},
            {"from": "hier_execute", "to": "hier_review"},
            {"from": "hier_review", "to": "hier_integrate"},
            {"from": "hier_integrate", "to": "hier_validate"}
        ]
        
        templates[CollaborationStrategy.HIERARCHICAL] = hierarchical_template
        
        # 競爭協作模板
        competitive_template = CollaborationFlow(
            flow_id="template_competitive",
            name="競爭協作模板",
            description="多個智能體競爭執行任務",
            strategy=CollaborationStrategy.COMPETITIVE
        )
        
        # 添加競爭協作節點
        competitive_nodes = [
            FlowNode("comp_brief", FlowNodeType.TASK, "任務簡報", "向所有參與者說明任務要求"),
            FlowNode("comp_compete", FlowNodeType.PARALLEL, "競爭執行", "多個智能體同時執行任務", 
                    dependencies=["comp_brief"]),
            FlowNode("comp_evaluate", FlowNodeType.DECISION, "結果評估", "評估各智能體的執行結果", 
                    dependencies=["comp_compete"]),
            FlowNode("comp_select", FlowNodeType.TASK, "最佳選擇", "選擇最佳執行結果", 
                    dependencies=["comp_evaluate"]),
            FlowNode("comp_learn", FlowNodeType.TASK, "經驗學習", "從競爭結果中學習改進", 
                    dependencies=["comp_select"])
        ]
        
        for node in competitive_nodes:
            competitive_template.nodes[node.node_id] = node
        
        competitive_template.edges = [
            {"from": "comp_brief", "to": "comp_compete"},
            {"from": "comp_compete", "to": "comp_evaluate"},
            {"from": "comp_evaluate", "to": "comp_select"},
            {"from": "comp_select", "to": "comp_learn"}
        ]
        
        templates[CollaborationStrategy.COMPETITIVE] = competitive_template
        
        return templates
    
    def _select_flow_template(self, strategy: CollaborationStrategy, 
                            task_characteristics: TaskCharacteristics) -> CollaborationFlow:
        """選擇流程模板"""
        
        base_template = self.flow_templates.get(strategy)
        if not base_template:
            # 如果沒有對應的模板，使用順序協作作為默認
            base_template = self.flow_templates[CollaborationStrategy.SEQUENTIAL]
        
        # 創建模板副本
        import copy
        return copy.deepcopy(base_template)
    
    async def _customize_flow_for_task(self, flow: CollaborationFlow, 
                                     task_characteristics: TaskCharacteristics) -> CollaborationFlow:
        """根據任務特徵定制流程"""
        
        # 根據任務複雜度調整流程
        if task_characteristics.complexity == TaskComplexity.SIMPLE:
            # 簡化流程，移除不必要的節點
            flow = self._simplify_flow(flow)
        elif task_characteristics.complexity == TaskComplexity.VERY_COMPLEX:
            # 增強流程，添加額外的檢查點和驗證節點
            flow = self._enhance_flow(flow)
        
        # 根據緊急程度調整節點優先級
        if task_characteristics.urgency in [TaskUrgency.HIGH, TaskUrgency.CRITICAL]:
            for node in flow.nodes.values():
                node.priority = min(node.priority + 1, 3)  # 提高優先級
                node.estimated_duration *= 0.8  # 縮短預估時間
        
        # 根據領域特徵添加專業化節點
        if task_characteristics.domain == "data_analysis":
            self._add_data_analysis_nodes(flow)
        elif task_characteristics.domain == "code_generation":
            self._add_code_generation_nodes(flow)
        elif task_characteristics.domain == "content_creation":
            self._add_content_creation_nodes(flow)
        
        return flow
    
    def _simplify_flow(self, flow: CollaborationFlow) -> CollaborationFlow:
        """簡化流程"""
        
        # 移除可選的檢查點和驗證節點
        nodes_to_remove = []
        for node_id, node in flow.nodes.items():
            if node.node_type in [FlowNodeType.CHECKPOINT] and node.priority < 2:
                nodes_to_remove.append(node_id)
        
        for node_id in nodes_to_remove:
            self._remove_node_safely(flow, node_id)
        
        return flow
    
    def _enhance_flow(self, flow: CollaborationFlow) -> CollaborationFlow:
        """增強流程"""
        
        # 添加額外的檢查點
        checkpoint_nodes = []
        for node_id, node in list(flow.nodes.items()):
            if node.node_type == FlowNodeType.TASK and node.estimated_duration > 120:
                # 為長時間任務添加中間檢查點
                checkpoint_id = f"{node_id}_checkpoint"
                checkpoint_node = FlowNode(
                    checkpoint_id, 
                    FlowNodeType.CHECKPOINT,
                    f"{node.name}檢查點",
                    f"檢查{node.name}的執行進度",
                    dependencies=[node_id],
                    estimated_duration=10.0
                )
                checkpoint_nodes.append(checkpoint_node)
        
        # 添加檢查點節點到流程中
        for checkpoint in checkpoint_nodes:
            flow.nodes[checkpoint.node_id] = checkpoint
            # 更新依賴關係
            self._insert_checkpoint_in_flow(flow, checkpoint)
        
        return flow
    
    def _add_data_analysis_nodes(self, flow: CollaborationFlow):
        """添加數據分析專業化節點"""
        
        # 添加數據驗證節點
        data_validation_node = FlowNode(
            "data_validation",
            FlowNodeType.TASK,
            "數據驗證",
            "驗證輸入數據的質量和完整性",
            estimated_duration=30.0,
            priority=2
        )
        
        # 添加結果可視化節點
        visualization_node = FlowNode(
            "data_visualization",
            FlowNodeType.TASK,
            "結果可視化",
            "創建數據分析結果的可視化圖表",
            estimated_duration=45.0,
            priority=1
        )
        
        flow.nodes[data_validation_node.node_id] = data_validation_node
        flow.nodes[visualization_node.node_id] = visualization_node
        
        # 更新流程結構，將數據驗證插入到開始位置
        self._insert_node_at_beginning(flow, data_validation_node)
        # 將可視化插入到結束位置
        self._insert_node_at_end(flow, visualization_node)
    
    def _add_code_generation_nodes(self, flow: CollaborationFlow):
        """添加代碼生成專業化節點"""
        
        # 添加代碼審查節點
        code_review_node = FlowNode(
            "code_review",
            FlowNodeType.TASK,
            "代碼審查",
            "審查生成代碼的質量和安全性",
            estimated_duration=60.0,
            priority=2
        )
        
        # 添加測試生成節點
        test_generation_node = FlowNode(
            "test_generation",
            FlowNodeType.TASK,
            "測試生成",
            "為生成的代碼創建單元測試",
            estimated_duration=40.0,
            priority=1
        )
        
        flow.nodes[code_review_node.node_id] = code_review_node
        flow.nodes[test_generation_node.node_id] = test_generation_node
        
        # 插入到適當位置
        self._insert_node_before_end(flow, code_review_node)
        self._insert_node_before_end(flow, test_generation_node)
    
    def _add_content_creation_nodes(self, flow: CollaborationFlow):
        """添加內容創作專業化節點"""
        
        # 添加內容審查節點
        content_review_node = FlowNode(
            "content_review",
            FlowNodeType.TASK,
            "內容審查",
            "審查創作內容的質量和準確性",
            estimated_duration=30.0,
            priority=2
        )
        
        # 添加格式優化節點
        format_optimization_node = FlowNode(
            "format_optimization",
            FlowNodeType.TASK,
            "格式優化",
            "優化內容的格式和排版",
            estimated_duration=20.0,
            priority=1
        )
        
        flow.nodes[content_review_node.node_id] = content_review_node
        flow.nodes[format_optimization_node.node_id] = format_optimization_node
        
        # 插入到適當位置
        self._insert_node_before_end(flow, content_review_node)
        self._insert_node_at_end(flow, format_optimization_node)
    
    async def _optimize_flow_for_agents(self, flow: CollaborationFlow, 
                                      agent_capabilities: List[AgentCapability]) -> CollaborationFlow:
        """根據智能體能力優化流程"""
        
        # 為每個節點分配最適合的智能體
        for node in flow.nodes.values():
            optimal_agents = self._find_optimal_agents_for_node(node, agent_capabilities)
            node.assigned_agents = [agent.agent_id for agent in optimal_agents[:2]]  # 最多分配2個智能體
        
        # 根據智能體負載調整並行度
        flow = self._adjust_parallelism_by_load(flow, agent_capabilities)
        
        # 根據智能體專業化調整任務分配
        flow = self._optimize_task_assignment(flow, agent_capabilities)
        
        return flow
    
    def _find_optimal_agents_for_node(self, node: FlowNode, 
                                    agent_capabilities: List[AgentCapability]) -> List[AgentCapability]:
        """為節點找到最優智能體"""
        
        # 根據節點類型和要求評分智能體
        scored_agents = []
        
        for agent in agent_capabilities:
            if not agent.availability:
                continue
            
            score = 0.0
            
            # 基於節點類型的適配性評分
            if node.node_type == FlowNodeType.TASK:
                # 任務節點需要執行能力強的智能體
                score += getattr(agent, 'overall_capability', 0.5) * 0.4
            elif node.node_type == FlowNodeType.DECISION:
                # 決策節點需要分析能力強的智能體
                score += agent.performance_scores.get('analysis', 0.5) * 0.4
            elif node.node_type == FlowNodeType.MERGE:
                # 合併節點需要整合能力強的智能體
                score += agent.performance_scores.get('integration', 0.5) * 0.4
            
            # 基於當前負載的評分
            load_factor = 1.0 - agent.current_load
            score += load_factor * 0.3
            
            # 基於協作歷史的評分
            collaboration_score = agent.collaboration_history.get("average_score", 0.7)
            score += collaboration_score * 0.3
            
            scored_agents.append((agent, score))
        
        # 按評分排序並返回
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return [agent for agent, score in scored_agents]
    
    def _adjust_parallelism_by_load(self, flow: CollaborationFlow, 
                                  agent_capabilities: List[AgentCapability]) -> CollaborationFlow:
        """根據智能體負載調整並行度"""
        
        # 計算可用智能體的平均負載
        available_agents = [agent for agent in agent_capabilities if agent.availability]
        if not available_agents:
            return flow
        
        avg_load = sum(agent.current_load for agent in available_agents) / len(available_agents)
        
        # 如果平均負載過高，減少並行節點
        if avg_load > 0.7:
            parallel_nodes = [node for node in flow.nodes.values() if node.node_type == FlowNodeType.PARALLEL]
            for node in parallel_nodes:
                # 將並行節點轉換為順序執行
                self._convert_parallel_to_sequential(flow, node)
        
        # 如果平均負載較低，增加並行機會
        elif avg_load < 0.3:
            sequential_chains = self._find_sequential_chains(flow)
            for chain in sequential_chains:
                if len(chain) > 2:
                    # 將部分順序節點轉換為並行執行
                    self._convert_sequential_to_parallel(flow, chain)
        
        return flow
    
    def _optimize_task_assignment(self, flow: CollaborationFlow, 
                                agent_capabilities: List[AgentCapability]) -> CollaborationFlow:
        """優化任務分配"""
        
        # 識別專業化智能體
        specialists = {}
        for agent in agent_capabilities:
            for specialization in agent.specializations:
                if specialization not in specialists:
                    specialists[specialization] = []
                specialists[specialization].append(agent)
        
        # 為需要專業技能的節點重新分配智能體
        for node in flow.nodes.values():
            if node.description:
                # 基於節點描述識別所需專業技能
                required_skills = self._extract_required_skills(node.description)
                
                for skill in required_skills:
                    if skill in specialists:
                        # 優先分配專業智能體
                        specialist_agents = specialists[skill]
                        available_specialists = [agent for agent in specialist_agents if agent.availability]
                        
                        if available_specialists:
                            # 選擇負載最低的專業智能體
                            best_specialist = min(available_specialists, key=lambda x: x.current_load)
                            if best_specialist.agent_id not in node.assigned_agents:
                                node.assigned_agents.insert(0, best_specialist.agent_id)
        
        return flow
    
    def _extract_required_skills(self, description: str) -> List[str]:
        """從描述中提取所需技能"""
        skill_keywords = {
            "data_analysis": ["分析", "數據", "統計", "圖表"],
            "code_generation": ["代碼", "編程", "開發", "函數"],
            "content_creation": ["內容", "寫作", "創作", "文檔"],
            "system_design": ["設計", "架構", "系統", "方案"],
            "optimization": ["優化", "改進", "提升", "效率"]
        }
        
        required_skills = []
        description_lower = description.lower()
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                required_skills.append(skill)
        
        return required_skills
    
    async def _add_adaptive_mechanisms(self, flow: CollaborationFlow) -> CollaborationFlow:
        """添加自適應機制"""
        
        # 為每個關鍵節點添加性能監控
        for node in flow.nodes.values():
            if node.node_type == FlowNodeType.TASK and node.estimated_duration > 60:
                # 添加性能監控回調
                node.performance_callbacks = [
                    self._monitor_node_performance,
                    self._check_quality_threshold,
                    self._detect_bottlenecks
                ]
        
        # 添加動態調整觸發器
        flow.adaptive_triggers = [
            {
                "condition": "node_duration_exceeded",
                "threshold": 1.5,  # 超過預估時間50%
                "action": "reassign_or_parallelize"
            },
            {
                "condition": "quality_below_threshold",
                "threshold": 0.7,
                "action": "add_review_step"
            },
            {
                "condition": "agent_overload",
                "threshold": 0.9,
                "action": "redistribute_load"
            }
        ]
        
        return flow
    
    # 輔助方法
    def _remove_node_safely(self, flow: CollaborationFlow, node_id: str):
        """安全移除節點"""
        if node_id not in flow.nodes:
            return
        
        # 更新邊連接
        incoming_edges = [edge for edge in flow.edges if edge["to"] == node_id]
        outgoing_edges = [edge for edge in flow.edges if edge["from"] == node_id]
        
        # 移除相關邊
        flow.edges = [edge for edge in flow.edges if edge["from"] != node_id and edge["to"] != node_id]
        
        # 重新連接前後節點
        for incoming in incoming_edges:
            for outgoing in outgoing_edges:
                flow.edges.append({"from": incoming["from"], "to": outgoing["to"]})
        
        # 移除節點
        del flow.nodes[node_id]
    
    def _insert_checkpoint_in_flow(self, flow: CollaborationFlow, checkpoint: FlowNode):
        """在流程中插入檢查點"""
        target_node_id = checkpoint.dependencies[0]
        
        # 找到目標節點的後續節點
        outgoing_edges = [edge for edge in flow.edges if edge["from"] == target_node_id]
        
        # 移除原有邊
        flow.edges = [edge for edge in flow.edges if edge["from"] != target_node_id]
        
        # 添加新邊：目標節點 -> 檢查點
        flow.edges.append({"from": target_node_id, "to": checkpoint.node_id})
        
        # 添加新邊：檢查點 -> 原後續節點
        for edge in outgoing_edges:
            flow.edges.append({"from": checkpoint.node_id, "to": edge["to"]})
    
    def _insert_node_at_beginning(self, flow: CollaborationFlow, node: FlowNode):
        """在流程開始位置插入節點"""
        # 找到沒有依賴的起始節點
        start_nodes = []
        all_targets = {edge["to"] for edge in flow.edges}
        
        for node_id in flow.nodes.keys():
            if node_id not in all_targets:
                start_nodes.append(node_id)
        
        # 將新節點連接到所有起始節點
        for start_node_id in start_nodes:
            flow.edges.append({"from": node.node_id, "to": start_node_id})
    
    def _insert_node_at_end(self, flow: CollaborationFlow, node: FlowNode):
        """在流程結束位置插入節點"""
        # 找到沒有後續的結束節點
        end_nodes = []
        all_sources = {edge["from"] for edge in flow.edges}
        
        for node_id in flow.nodes.keys():
            if node_id not in all_sources:
                end_nodes.append(node_id)
        
        # 將所有結束節點連接到新節點
        for end_node_id in end_nodes:
            flow.edges.append({"from": end_node_id, "to": node.node_id})
    
    def _insert_node_before_end(self, flow: CollaborationFlow, node: FlowNode):
        """在流程結束前插入節點"""
        # 找到結束節點
        end_nodes = []
        all_sources = {edge["from"] for edge in flow.edges}
        
        for node_id in flow.nodes.keys():
            if node_id not in all_sources:
                end_nodes.append(node_id)
        
        if end_nodes:
            # 選擇第一個結束節點作為目標
            target_end_node = end_nodes[0]
            
            # 找到指向結束節點的邊
            incoming_edges = [edge for edge in flow.edges if edge["to"] == target_end_node]
            
            # 移除指向結束節點的邊
            flow.edges = [edge for edge in flow.edges if edge["to"] != target_end_node]
            
            # 重新連接：前置節點 -> 新節點 -> 結束節點
            for edge in incoming_edges:
                flow.edges.append({"from": edge["from"], "to": node.node_id})
            
            flow.edges.append({"from": node.node_id, "to": target_end_node})
    
    # 性能監控回調函數
    async def _monitor_node_performance(self, node: FlowNode, context: Dict[str, Any]):
        """監控節點性能"""
        if node.start_time:
            current_duration = time.time() - node.start_time
            if current_duration > node.estimated_duration * 1.2:
                # 執行時間超出預期20%，觸發警告
                context["performance_warnings"].append({
                    "node_id": node.node_id,
                    "issue": "duration_exceeded",
                    "current_duration": current_duration,
                    "estimated_duration": node.estimated_duration
                })
    
    async def _check_quality_threshold(self, node: FlowNode, context: Dict[str, Any]):
        """檢查質量閾值"""
        if node.quality_score and node.quality_score < 0.7:
            context["quality_warnings"].append({
                "node_id": node.node_id,
                "issue": "quality_below_threshold",
                "quality_score": node.quality_score,
                "threshold": 0.7
            })
    
    async def _detect_bottlenecks(self, node: FlowNode, context: Dict[str, Any]):
        """檢測瓶頸"""
        if node.resource_usage.get("cpu", 0) > 0.9:
            context["bottleneck_warnings"].append({
                "node_id": node.node_id,
                "issue": "cpu_bottleneck",
                "cpu_usage": node.resource_usage["cpu"]
            })
```

這個協作流程動態重構引擎提供了強大的流程定制和優化能力。它能夠根據任務特徵、智能體能力和實時執行狀況動態調整協作流程，確保協作效率的最大化。

通過這種設計，PowerAutomation將能夠：

1. **根據任務複雜度動態調整流程結構** - 簡單任務使用簡化流程，複雜任務增加檢查點和驗證步驟
2. **基於智能體專業化優化任務分配** - 將任務分配給最適合的專業智能體
3. **實時監控和調整協作流程** - 基於執行狀況動態重構流程結構
4. **支援多種協作模式** - 順序、並行、階層、競爭等多種協作策略

這種動態流程重構能力是實現L4級別多智能體協作的關鍵技術，它使得PowerAutomation能夠靈活應對各種協作場景和需求變化。

