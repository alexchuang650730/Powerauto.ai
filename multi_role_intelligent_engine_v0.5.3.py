#!/usr/bin/env python3
"""
PowerAutomation v0.5.3 多角色智能引擎實現
實現2B企業、2C個人、開源社區三種差異化智能引擎
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib
import threading
from pathlib import Path

# 導入v0.5.2的智能引擎組件
try:
    from dynamic_network_manager import DynamicNetworkManager
    from mcptool.adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP
    from mcptool.adapters.unified_smart_tool_engine_mcp import UnifiedSmartToolEngineMCP
    from mcptool.adapters.smart_fallback_system_v2 import SearchEngineFallbackSystem
    from mcptool.adapters.smart_routing_mcp import SmartRoutingMCP
except ImportError:
    # Mock實現用於測試
    class DynamicNetworkManager:
        def get_config_info(self): return {"status": "mock"}
    class IntelligentWorkflowEngineMCP:
        def process(self, data): return {"result": "mock"}
    class UnifiedSmartToolEngineMCP:
        def process(self, data): return {"result": "mock"}
    class SearchEngineFallbackSystem:
        def process(self, data): return {"result": "mock"}
    class SmartRoutingMCP:
        def process(self, data): return {"result": "mock"}


class UserRole(Enum):
    """用戶角色枚舉"""
    ENTERPRISE_2B = "enterprise_2b"
    PERSONAL_2C = "personal_2c"
    OPENSOURCE = "opensource"
    UNKNOWN = "unknown"


@dataclass
class RoleContext:
    """角色上下文數據"""
    role: UserRole
    user_id: str
    session_id: str
    preferences: Dict[str, Any]
    history: List[Dict[str, Any]]
    security_level: str
    permissions: List[str]
    created_at: datetime
    last_active: datetime


@dataclass
class ProcessingRequest:
    """處理請求數據"""
    request_id: str
    user_id: str
    role: UserRole
    content: str
    context: Dict[str, Any]
    timestamp: datetime
    priority: int = 1
    metadata: Dict[str, Any] = None


@dataclass
class ProcessingResult:
    """處理結果數據"""
    request_id: str
    success: bool
    result: Any
    role_specific_data: Dict[str, Any]
    processing_time: float
    confidence: float
    recommendations: List[str]
    next_actions: List[str]


class RoleIdentifier:
    """角色識別器"""
    
    def __init__(self):
        self.logger = logging.getLogger("RoleIdentifier")
        self.identification_patterns = {
            UserRole.ENTERPRISE_2B: {
                "keywords": ["企業", "團隊", "合規", "審批", "報告", "CRM", "ERP", "workflow", "enterprise"],
                "time_patterns": ["09:00-18:00"],
                "complexity_threshold": 0.8,
                "security_requirements": ["high", "enterprise"]
            },
            UserRole.PERSONAL_2C: {
                "keywords": ["個人", "家庭", "娛樂", "學習", "生活", "個人助手", "日程", "提醒"],
                "time_patterns": ["全天"],
                "complexity_threshold": 0.5,
                "security_requirements": ["medium", "personal"]
            },
            UserRole.OPENSOURCE: {
                "keywords": ["開源", "社區", "貢獻", "協作", "代碼", "GitHub", "開發", "API"],
                "time_patterns": ["項目驅動"],
                "complexity_threshold": 0.9,
                "security_requirements": ["transparent", "open"]
            }
        }
        
    def identify_role(self, request: str, user_context: Dict = None) -> Tuple[UserRole, float]:
        """識別用戶角色"""
        scores = {}
        
        for role, patterns in self.identification_patterns.items():
            score = 0.0
            
            # 關鍵詞匹配
            keyword_matches = sum(1 for keyword in patterns["keywords"] 
                                if keyword.lower() in request.lower())
            score += keyword_matches * 0.3
            
            # 用戶上下文分析
            if user_context:
                if user_context.get("domain") in patterns.get("domains", []):
                    score += 0.4
                if user_context.get("security_level") in patterns["security_requirements"]:
                    score += 0.3
            
            scores[role] = min(score, 1.0)
        
        # 選擇最高分的角色
        best_role = max(scores.items(), key=lambda x: x[1])
        
        if best_role[1] < 0.3:
            return UserRole.UNKNOWN, best_role[1]
        
        return best_role[0], best_role[1]


class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("ContextManager")
        self.contexts: Dict[str, RoleContext] = {}
        self.context_lock = threading.Lock()
        
    def create_context(self, user_id: str, role: UserRole, 
                      preferences: Dict = None) -> RoleContext:
        """創建角色上下文"""
        with self.context_lock:
            session_id = str(uuid.uuid4())
            context = RoleContext(
                role=role,
                user_id=user_id,
                session_id=session_id,
                preferences=preferences or {},
                history=[],
                security_level=self._get_security_level(role),
                permissions=self._get_permissions(role),
                created_at=datetime.now(),
                last_active=datetime.now()
            )
            
            self.contexts[session_id] = context
            self.logger.info(f"創建角色上下文: {role.value} for user {user_id}")
            return context
    
    def get_context(self, session_id: str) -> Optional[RoleContext]:
        """獲取角色上下文"""
        with self.context_lock:
            context = self.contexts.get(session_id)
            if context:
                context.last_active = datetime.now()
            return context
    
    def update_context(self, session_id: str, updates: Dict[str, Any]):
        """更新角色上下文"""
        with self.context_lock:
            if session_id in self.contexts:
                context = self.contexts[session_id]
                for key, value in updates.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
                context.last_active = datetime.now()
    
    def _get_security_level(self, role: UserRole) -> str:
        """獲取安全級別"""
        security_levels = {
            UserRole.ENTERPRISE_2B: "high",
            UserRole.PERSONAL_2C: "medium",
            UserRole.OPENSOURCE: "transparent"
        }
        return security_levels.get(role, "low")
    
    def _get_permissions(self, role: UserRole) -> List[str]:
        """獲取權限列表"""
        permissions = {
            UserRole.ENTERPRISE_2B: [
                "enterprise_tools", "team_collaboration", "compliance_check",
                "audit_log", "advanced_security", "enterprise_integration"
            ],
            UserRole.PERSONAL_2C: [
                "personal_tools", "life_integration", "entertainment",
                "learning_assistance", "smart_recommendations"
            ],
            UserRole.OPENSOURCE: [
                "development_tools", "community_collaboration", "code_generation",
                "open_apis", "transparency_tools", "contribution_tracking"
            ]
        }
        return permissions.get(role, [])


class BaseRoleEngine(ABC):
    """角色引擎基類"""
    
    def __init__(self, role: UserRole):
        self.role = role
        self.logger = logging.getLogger(f"{role.value}Engine")
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "user_satisfaction": 0.0
        }
        
        # 集成v0.5.2智能引擎組件
        self.workflow_engine = IntelligentWorkflowEngineMCP()
        self.tool_engine = UnifiedSmartToolEngineMCP()
        self.fallback_system = SearchEngineFallbackSystem()
        self.routing_system = SmartRoutingMCP()
    
    @abstractmethod
    async def process_request(self, request: ProcessingRequest, 
                            context: RoleContext) -> ProcessingResult:
        """處理請求的抽象方法"""
        pass
    
    @abstractmethod
    def get_role_specific_tools(self) -> List[str]:
        """獲取角色特定工具"""
        pass
    
    @abstractmethod
    def customize_user_experience(self, context: RoleContext) -> Dict[str, Any]:
        """定制用戶體驗"""
        pass
    
    def update_metrics(self, processing_time: float, success: bool, satisfaction: float = None):
        """更新性能指標"""
        self.performance_metrics["total_requests"] += 1
        if success:
            self.performance_metrics["successful_requests"] += 1
        
        # 更新平均響應時間
        total = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # 更新用戶滿意度
        if satisfaction is not None:
            current_satisfaction = self.performance_metrics["user_satisfaction"]
            self.performance_metrics["user_satisfaction"] = (
                (current_satisfaction * (total - 1) + satisfaction) / total
            )


class EnterpriseEngine(BaseRoleEngine):
    """2B企業引擎"""
    
    def __init__(self):
        super().__init__(UserRole.ENTERPRISE_2B)
        self.security_manager = EnterpriseSecurityManager()
        self.compliance_checker = ComplianceChecker()
        self.team_coordinator = TeamCoordinator()
        self.enterprise_integrator = EnterpriseIntegrator()
    
    async def process_request(self, request: ProcessingRequest, 
                            context: RoleContext) -> ProcessingResult:
        """處理企業請求"""
        start_time = time.time()
        
        try:
            # 企業級安全檢查
            security_result = await self.security_manager.validate_request(request, context)
            if not security_result["valid"]:
                return ProcessingResult(
                    request_id=request.request_id,
                    success=False,
                    result={"error": "安全檢查失敗", "details": security_result},
                    role_specific_data={"security_violation": True},
                    processing_time=time.time() - start_time,
                    confidence=0.0,
                    recommendations=["請聯繫系統管理員"],
                    next_actions=["security_review"]
                )
            
            # 合規性檢查
            compliance_result = await self.compliance_checker.verify_compliance(request, context)
            
            # 團隊協作處理
            team_result = await self.team_coordinator.coordinate_team_action(request, context)
            
            # 企業工具集成
            integration_result = await self.enterprise_integrator.execute_enterprise_workflow(
                request, context, security_result, compliance_result, team_result
            )
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                request_id=request.request_id,
                success=True,
                result=integration_result,
                role_specific_data={
                    "security_level": security_result.get("level"),
                    "compliance_status": compliance_result.get("status"),
                    "team_involvement": team_result.get("team_members", []),
                    "enterprise_tools_used": integration_result.get("tools_used", [])
                },
                processing_time=processing_time,
                confidence=integration_result.get("confidence", 0.8),
                recommendations=self._generate_enterprise_recommendations(integration_result),
                next_actions=self._generate_enterprise_next_actions(integration_result)
            )
            
            self.update_metrics(processing_time, True)
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"企業請求處理失敗: {e}")
            self.update_metrics(processing_time, False)
            
            return ProcessingResult(
                request_id=request.request_id,
                success=False,
                result={"error": str(e)},
                role_specific_data={"error_type": "processing_error"},
                processing_time=processing_time,
                confidence=0.0,
                recommendations=["請重試或聯繫技術支持"],
                next_actions=["retry", "contact_support"]
            )
    
    def get_role_specific_tools(self) -> List[str]:
        """獲取企業特定工具"""
        return [
            "crm_integration", "erp_connector", "compliance_checker",
            "security_auditor", "team_collaboration", "enterprise_reporting",
            "workflow_automation", "document_management", "access_control"
        ]
    
    def customize_user_experience(self, context: RoleContext) -> Dict[str, Any]:
        """定制企業用戶體驗"""
        return {
            "interface_theme": "professional",
            "security_indicators": True,
            "compliance_alerts": True,
            "team_collaboration_panel": True,
            "enterprise_dashboard": True,
            "audit_trail": True,
            "advanced_permissions": True
        }
    
    def _generate_enterprise_recommendations(self, result: Dict) -> List[str]:
        """生成企業建議"""
        recommendations = []
        
        if result.get("efficiency_score", 0) < 0.8:
            recommendations.append("建議優化工作流程以提高效率")
        
        if result.get("security_score", 0) < 0.9:
            recommendations.append("建議加強安全措施")
        
        if result.get("team_collaboration_score", 0) < 0.7:
            recommendations.append("建議改善團隊協作流程")
        
        return recommendations
    
    def _generate_enterprise_next_actions(self, result: Dict) -> List[str]:
        """生成企業下一步行動"""
        actions = []
        
        if result.get("requires_approval"):
            actions.append("submit_for_approval")
        
        if result.get("needs_team_review"):
            actions.append("schedule_team_review")
        
        if result.get("compliance_follow_up"):
            actions.append("compliance_follow_up")
        
        return actions


class PersonalEngine(BaseRoleEngine):
    """2C個人引擎"""
    
    def __init__(self):
        super().__init__(UserRole.PERSONAL_2C)
        self.personalization_manager = PersonalizationManager()
        self.simplification_engine = SimplificationEngine()
        self.recommendation_system = RecommendationSystem()
        self.life_integrator = LifeIntegrator()
    
    async def process_request(self, request: ProcessingRequest, 
                            context: RoleContext) -> ProcessingResult:
        """處理個人請求"""
        start_time = time.time()
        
        try:
            # 個性化處理
            personalized_request = await self.personalization_manager.customize_request(
                request, context
            )
            
            # 操作簡化
            simplified_request = await self.simplification_engine.simplify_operation(
                personalized_request, context
            )
            
            # 智能推薦
            recommendations = await self.recommendation_system.generate_recommendations(
                simplified_request, context
            )
            
            # 生活集成
            life_integration_result = await self.life_integrator.integrate_with_life(
                simplified_request, context, recommendations
            )
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                request_id=request.request_id,
                success=True,
                result=life_integration_result,
                role_specific_data={
                    "personalization_applied": personalized_request.get("customizations", []),
                    "simplifications_made": simplified_request.get("simplifications", []),
                    "life_integrations": life_integration_result.get("integrations", []),
                    "user_preferences_learned": context.preferences
                },
                processing_time=processing_time,
                confidence=life_integration_result.get("confidence", 0.85),
                recommendations=recommendations.get("suggestions", []),
                next_actions=self._generate_personal_next_actions(life_integration_result)
            )
            
            self.update_metrics(processing_time, True)
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"個人請求處理失敗: {e}")
            self.update_metrics(processing_time, False)
            
            return ProcessingResult(
                request_id=request.request_id,
                success=False,
                result={"error": str(e)},
                role_specific_data={"error_type": "processing_error"},
                processing_time=processing_time,
                confidence=0.0,
                recommendations=["請嘗試重新表述您的請求"],
                next_actions=["retry", "get_help"]
            )
    
    def get_role_specific_tools(self) -> List[str]:
        """獲取個人特定工具"""
        return [
            "personal_assistant", "calendar_management", "smart_reminders",
            "life_optimization", "entertainment_recommendations", "learning_assistant",
            "health_tracker", "finance_manager", "smart_home_integration",
            "social_media_manager", "travel_planner"
        ]
    
    def customize_user_experience(self, context: RoleContext) -> Dict[str, Any]:
        """定制個人用戶體驗"""
        return {
            "interface_theme": "friendly",
            "personalization_level": "high",
            "simplification_enabled": True,
            "smart_suggestions": True,
            "life_integration_panel": True,
            "entertainment_recommendations": True,
            "learning_progress_tracking": True
        }
    
    def _generate_personal_next_actions(self, result: Dict) -> List[str]:
        """生成個人下一步行動"""
        actions = []
        
        if result.get("schedule_follow_up"):
            actions.append("schedule_reminder")
        
        if result.get("learning_opportunity"):
            actions.append("explore_learning")
        
        if result.get("optimization_suggestion"):
            actions.append("apply_optimization")
        
        return actions


class OpenSourceEngine(BaseRoleEngine):
    """開源社區引擎"""
    
    def __init__(self):
        super().__init__(UserRole.OPENSOURCE)
        self.collaboration_manager = CollaborationManager()
        self.community_governor = CommunityGovernor()
        self.transparency_manager = TransparencyManager()
        self.developer_toolkit = DeveloperToolkit()
    
    async def process_request(self, request: ProcessingRequest, 
                            context: RoleContext) -> ProcessingResult:
        """處理開源請求"""
        start_time = time.time()
        
        try:
            # 社區協作處理
            collaboration_result = await self.collaboration_manager.facilitate_collaboration(
                request, context
            )
            
            # 社區治理
            governance_result = await self.community_governor.apply_governance(
                request, context
            )
            
            # 透明度管理
            transparency_result = await self.transparency_manager.ensure_transparency(
                request, context, collaboration_result, governance_result
            )
            
            # 開發者工具包
            developer_result = await self.developer_toolkit.execute_development_task(
                request, context, transparency_result
            )
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                request_id=request.request_id,
                success=True,
                result=developer_result,
                role_specific_data={
                    "community_involvement": collaboration_result.get("participants", []),
                    "governance_applied": governance_result.get("rules_applied", []),
                    "transparency_level": transparency_result.get("transparency_score", 1.0),
                    "open_source_contributions": developer_result.get("contributions", []),
                    "code_generated": developer_result.get("code_artifacts", [])
                },
                processing_time=processing_time,
                confidence=developer_result.get("confidence", 0.9),
                recommendations=self._generate_opensource_recommendations(developer_result),
                next_actions=self._generate_opensource_next_actions(developer_result)
            )
            
            self.update_metrics(processing_time, True)
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"開源請求處理失敗: {e}")
            self.update_metrics(processing_time, False)
            
            return ProcessingResult(
                request_id=request.request_id,
                success=False,
                result={"error": str(e)},
                role_specific_data={"error_type": "processing_error"},
                processing_time=processing_time,
                confidence=0.0,
                recommendations=["請查看社區文檔或尋求社區幫助"],
                next_actions=["check_docs", "ask_community"]
            )
    
    def get_role_specific_tools(self) -> List[str]:
        """獲取開源特定工具"""
        return [
            "code_generator", "api_designer", "documentation_generator",
            "community_collaboration", "version_control", "continuous_integration",
            "open_source_license_manager", "contribution_tracker", "issue_manager",
            "pull_request_assistant", "code_review_helper"
        ]
    
    def customize_user_experience(self, context: RoleContext) -> Dict[str, Any]:
        """定制開源用戶體驗"""
        return {
            "interface_theme": "developer",
            "transparency_level": "full",
            "community_features": True,
            "collaboration_tools": True,
            "code_sharing": True,
            "contribution_tracking": True,
            "open_documentation": True
        }
    
    def _generate_opensource_recommendations(self, result: Dict) -> List[str]:
        """生成開源建議"""
        recommendations = []
        
        if result.get("code_quality_score", 0) < 0.8:
            recommendations.append("建議改進代碼質量和文檔")
        
        if result.get("community_engagement", 0) < 0.7:
            recommendations.append("建議增加社區參與和貢獻")
        
        if result.get("test_coverage", 0) < 0.9:
            recommendations.append("建議增加測試覆蓋率")
        
        return recommendations
    
    def _generate_opensource_next_actions(self, result: Dict) -> List[str]:
        """生成開源下一步行動"""
        actions = []
        
        if result.get("needs_community_review"):
            actions.append("submit_for_community_review")
        
        if result.get("ready_for_contribution"):
            actions.append("create_pull_request")
        
        if result.get("documentation_needed"):
            actions.append("update_documentation")
        
        return actions


# Mock實現的支持類
class EnterpriseSecurityManager:
    async def validate_request(self, request, context):
        return {"valid": True, "level": "high", "checks_passed": ["auth", "encryption", "audit"]}

class ComplianceChecker:
    async def verify_compliance(self, request, context):
        return {"status": "compliant", "standards": ["GDPR", "SOX", "ISO27001"]}

class TeamCoordinator:
    async def coordinate_team_action(self, request, context):
        return {"team_members": ["user1", "user2"], "coordination_success": True}

class EnterpriseIntegrator:
    async def execute_enterprise_workflow(self, request, context, security, compliance, team):
        return {
            "result": "企業工作流執行成功",
            "tools_used": ["CRM", "ERP", "Document Management"],
            "confidence": 0.9,
            "efficiency_score": 0.85
        }

class PersonalizationManager:
    async def customize_request(self, request, context):
        return {"customizations": ["ui_theme", "language_preference"], "request": request}

class SimplificationEngine:
    async def simplify_operation(self, request, context):
        return {"simplifications": ["one_click_action", "auto_complete"], "request": request}

class RecommendationSystem:
    async def generate_recommendations(self, request, context):
        return {"suggestions": ["相關功能推薦", "使用技巧", "個性化設置"]}

class LifeIntegrator:
    async def integrate_with_life(self, request, context, recommendations):
        return {
            "result": "生活集成成功",
            "integrations": ["calendar", "smart_home", "health_tracker"],
            "confidence": 0.88
        }

class CollaborationManager:
    async def facilitate_collaboration(self, request, context):
        return {"participants": ["developer1", "contributor2"], "collaboration_score": 0.9}

class CommunityGovernor:
    async def apply_governance(self, request, context):
        return {"rules_applied": ["code_of_conduct", "contribution_guidelines"], "governance_score": 0.95}

class TransparencyManager:
    async def ensure_transparency(self, request, context, collaboration, governance):
        return {"transparency_score": 1.0, "public_data": True, "open_process": True}

class DeveloperToolkit:
    async def execute_development_task(self, request, context, transparency):
        return {
            "result": "開發任務執行成功",
            "contributions": ["code_commit", "documentation_update"],
            "code_artifacts": ["main.py", "README.md"],
            "confidence": 0.92
        }


class MultiRoleIntelligentEngine:
    """多角色智能引擎主控制器"""
    
    def __init__(self):
        self.logger = logging.getLogger("MultiRoleIntelligentEngine")
        
        # 初始化組件
        self.role_identifier = RoleIdentifier()
        self.context_manager = ContextManager()
        
        # 初始化角色引擎
        self.engines = {
            UserRole.ENTERPRISE_2B: EnterpriseEngine(),
            UserRole.PERSONAL_2C: PersonalEngine(),
            UserRole.OPENSOURCE: OpenSourceEngine()
        }
        
        # 性能監控
        self.global_metrics = {
            "total_requests": 0,
            "role_distribution": {role.value: 0 for role in UserRole},
            "average_processing_time": 0.0,
            "success_rate": 0.0
        }
        
        self.logger.info("多角色智能引擎初始化完成")
    
    async def process_request(self, content: str, user_id: str, 
                            user_context: Dict = None) -> ProcessingResult:
        """處理用戶請求"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # 角色識別
            role, confidence = self.role_identifier.identify_role(content, user_context)
            
            if role == UserRole.UNKNOWN:
                # 默認使用個人引擎
                role = UserRole.PERSONAL_2C
                self.logger.warning(f"無法識別角色，使用默認個人引擎")
            
            # 獲取或創建上下文
            context = self.context_manager.create_context(user_id, role, user_context)
            
            # 創建處理請求
            processing_request = ProcessingRequest(
                request_id=request_id,
                user_id=user_id,
                role=role,
                content=content,
                context=user_context or {},
                timestamp=datetime.now(),
                priority=1,
                metadata={"role_confidence": confidence}
            )
            
            # 使用對應的角色引擎處理
            engine = self.engines[role]
            result = await engine.process_request(processing_request, context)
            
            # 更新全局指標
            self._update_global_metrics(role, time.time() - start_time, result.success)
            
            self.logger.info(f"請求處理完成: {request_id}, 角色: {role.value}, 成功: {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"請求處理失敗: {e}")
            return ProcessingResult(
                request_id=request_id,
                success=False,
                result={"error": str(e)},
                role_specific_data={},
                processing_time=time.time() - start_time,
                confidence=0.0,
                recommendations=["請重試或聯繫技術支持"],
                next_actions=["retry"]
            )
    
    def _update_global_metrics(self, role: UserRole, processing_time: float, success: bool):
        """更新全局性能指標"""
        self.global_metrics["total_requests"] += 1
        self.global_metrics["role_distribution"][role.value] += 1
        
        # 更新平均處理時間
        total = self.global_metrics["total_requests"]
        current_avg = self.global_metrics["average_processing_time"]
        self.global_metrics["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # 更新成功率
        if success:
            current_success_rate = self.global_metrics["success_rate"]
            self.global_metrics["success_rate"] = (
                (current_success_rate * (total - 1) + 1.0) / total
            )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """獲取引擎狀態"""
        status = {
            "global_metrics": self.global_metrics,
            "role_engines": {}
        }
        
        for role, engine in self.engines.items():
            status["role_engines"][role.value] = {
                "performance_metrics": engine.performance_metrics,
                "available_tools": engine.get_role_specific_tools()
            }
        
        return status
    
    def get_role_recommendations(self, user_id: str) -> Dict[str, Any]:
        """獲取角色建議"""
        # 這裡可以基於用戶歷史使用情況提供角色切換建議
        return {
            "current_role": "personal_2c",  # 示例
            "suggested_roles": ["enterprise_2b"],
            "reasons": ["檢測到企業相關關鍵詞"]
        }


# 使用示例
async def main():
    """主函數示例"""
    engine = MultiRoleIntelligentEngine()
    
    # 測試不同角色的請求
    test_requests = [
        {
            "content": "幫我分析公司的CRM數據並生成合規報告",
            "user_id": "enterprise_user_001",
            "context": {"domain": "enterprise", "security_level": "high"}
        },
        {
            "content": "提醒我明天下午3點開會，並推薦一些放鬆的音樂",
            "user_id": "personal_user_001", 
            "context": {"domain": "personal", "preferences": {"music": "classical"}}
        },
        {
            "content": "幫我生成一個開源項目的API文檔並提交到GitHub",
            "user_id": "opensource_user_001",
            "context": {"domain": "opensource", "github_username": "developer123"}
        }
    ]
    
    for req in test_requests:
        print(f"\n處理請求: {req['content'][:50]}...")
        result = await engine.process_request(
            req["content"], 
            req["user_id"], 
            req["context"]
        )
        print(f"結果: 成功={result.success}, 角色數據={result.role_specific_data}")
    
    # 顯示引擎狀態
    status = engine.get_engine_status()
    print(f"\n引擎狀態: {json.dumps(status, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

