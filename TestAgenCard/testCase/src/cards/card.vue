<template>
  <div class="testSpot" v-loading="apiLoading">
    <div class="title-header" v-if="data?.title">
      <div class="title-detail">{{ data?.title }}</div>
      <d-alert v-if="linkUrl" style="margin-top: 12px; background: #f5f7fa;" type="info" :closeable="false">
        归档地址:
        <d-link style="margin-left: 4px;" @click="handlelinkTo" target="_blank">{{ linkUrl }}</d-link>
      </d-alert>
      <div class="test-count">
        <div class="header-left">
          <div class="count-info">
            <span>测试用例总数：{{ getCaseTotal }}</span>&nbsp;|&nbsp;<span>测试点总数：{{ getTpTotal }}</span>
          </div>

          <div class="project-dir" v-if="projectName" :title="projectName">
            ( 项目：<span class="project-name">{{ projectName }}</span>
            <d-icon 
              name="edit-3" 
              operable 
              size="14px" 
              @click="handleEditProjectDir"
              style="margin-left: 4px; cursor: pointer;"
            ></d-icon>)
          </div>
        </div>

        <div class="operation-button-box">
          <!-- <d-button @click="handlelinkTo" bsStyle="primary" id="primaryBtn">跳转脑图</d-button> -->
          <d-button :loading="arChiveLoading" @click="handleArchive" bsStyle="primary" id="primaryBtn">归档至测试设计脑图</d-button>
          <d-button :disabled="!selectData.length" @click="handleArchiveTmss" id="archiveTmssBtn">归档至测试用例管理</d-button>
          <d-dropdown trigger="hover">
            <d-button>生成测试脚本</d-button>
            <template #menu>
              <div class="ide-dropdown-menu">
                <div class="ide-item" @click="handleOpenIDE('pycharm')">使用PyCharm编辑器</div>
                <div class="ide-item" @click="handleOpenIDE('vscodehuawei')">使用VSCode编辑器</div>
                <div class="ide-item" @click="handleOpenIDE('idea')">使用IDEA编辑器</div>
              </div>
            </template>
          </d-dropdown>
          <d-tooltip :max-width="1200">
            <template #content>
              <div ref="filePathRef">{{data?.saved_file_path}}</div>
            </template>
            <d-button @click="copyToClipboard" v-if="data?.saved_file_path" bsStyle="primary"
              id="primaryBtn">复制文档路径</d-button>
          </d-tooltip>
          <d-button :disabled="!redoCount" class="next-setp" variant="solid" @click="handleReDoCard"
            color="primary">重新生成</d-button>
          <d-button v-if="isEdit" title="保存用例" class="next-setp" variant="solid" @click="handleSaveCase"
            color="primary">保存</d-button>
        </div>
      </div>
    </div>

    <div :class="{ 'test-spot-list-show-link': linkUrl }" class="test-spot-list" v-if="data?.test_point_list">
      <div class="left-lsit">
        <div @click="handleChangeItem(item)" class="list-item" :class="item.isShow && 'list-item-show'"
          v-for="item in (data?.test_point_list || [])">
          <div class="item-title-content">
            <span class="item-icon"></span>
            <span class="item-title" :title="item.name">{{ item.name }}</span>
            <d-dropdown style="width: 120px;" place-strategy="no-space">
              <i @click.stop="item.isShow = true" style="color: #999; margin-left: 4px;"
                class="icon icon-more-operate"></i>
              <template #menu>
                <div class="testSpot-operation-button">
                  <div class="operation-item" @click="handleAddTestSpot(item)">
                    新增测试用例
                  </div>
                  <!-- <div class="operation-item" @click="handleOpenEdit(item)">
                    编辑
                  </div>
                  <div class="operation-item" @click="handleDelete(index)">
                    删除
                  </div> -->
                </div>
              </template>
            </d-dropdown>
          </div>
          <div class="item-children" v-if="item.isShow">
            <div @click.stop="handleChangeItem(child)" class="children-item"
              :class="[child.priority, ((currentData === child) && 'current-child')]"
              v-for="(child, childInd) in (item?.test_case_list || [])">
              <d-checkbox label=" " :isShowTitle="false" v-model="child.isCheck" />
              <span class="item-title" :title="child.name">{{ child.name }}</span>
              <span class="child-classFy">{{ child.priority }}</span>
              <span v-if="child.tmssArchivedStatus" class="child-classFy" style="color: #52c41a; background: #f6ffed; border-color: #b7eb8f;">已归档</span>
              <d-dropdown style="width: 100px;" place-strategy="no-space">
                <!-- <d-button>Click Me</d-button> -->
                <i style="color: #999; margin-left: 4px; font-size: 14px;" class="icon icon-more-operate"></i>
                <template #menu>
                  <div class="testSpot-operation-button">
                    <div class="operation-item" @click="handleOpenEditTestSpot(child)">
                      编辑
                    </div>
                    <div class="operation-item" @click="handleDelete(item?.test_case_list, childInd)">
                      删除
                    </div>
                  </div>
                </template>
              </d-dropdown>
            </div>
          </div>

        </div>
      </div>
      <div class="right-content">
        <div class="right-detail">
          <div class="right-header">
            <d-tooltip :position="'top'" :max-width="800" :append-to-body="true">
              <template #content><div class="tips-height">{{ currentData.name }}</div></template>
              <span class="detail-title">{{ currentData.name }}</span>
            </d-tooltip>
            <div class="detail-header-info">
              <d-tooltip :position="'top'" :max-width="800" :append-to-body="true">
                <template #content><div class="tips-height">{{ currentData.number }}</div></template>
                <span class="number-container">
                  <span class="info-title">用例编号：</span><span>{{ currentData.number }}</span>
                </span>
              </d-tooltip>
              <span><span style="margin-left: 12px;" class="info-title">用例等级：</span><span class="info-classFy">{{
                currentData.priority
              }}</span></span>
              <!-- 目前只在cida上展示 -->
              <span v-if="isCidaApp">
                <span style="margin-left: 12px;" class="info-title">测试类型：</span>
                <span class="info-type">{{ currentData.type }}</span>
              </span>
            </div>
          </div>
          <div class="right-container">
            <div class="content-section">
              <div style="margin-top: 0;" class="contain-name">预置条件
                <d-button variant="solid" color="primary" style="float: right;" @click="useCaseAnalysis">用例执行</d-button>
              </div>
              <div class="section-content">
                <template v-if="currentData.pre">
                  <div class="contain-value-text" :title="currentData.pre">{{ currentData.pre }}</div>
                </template>
                <dp-nodata v-else message="没有查询到数据" size="sm"></dp-nodata>
              </div>
            </div>
            
            <div class="content-section">
              <div class="contain-name">测试步骤</div>
              <div class="section-content">
                <template v-if="currentData.test_step">
                  <div class="contain-value-text" :title="currentData.test_step">{{ currentData.test_step }}</div>
                </template>
                <dp-nodata v-else message="没有查询到数据" size="sm"></dp-nodata>
              </div>
            </div>
            
            <div class="content-section">
              <div class="contain-name">预期结果</div>
              <div class="section-content">
                <template v-if="currentData.expect_output">
                  <div class="contain-value-text" :title="currentData.expect_output">{{ currentData.expect_output }}</div>
                </template>
                <dp-nodata v-else message="没有查询到数据" size="sm"></dp-nodata>
              </div>
            </div>
          </div>
        </div>
        <!-- <dp-nodata style="width: 33%;" v-else message="没有查询到数据" vertical-center></dp-nodata> -->
      </div>
    </div>
    <dp-nodata v-else message="没有查询到数据" vertical-center></dp-nodata>

    <!-- <d-button variant="solid" @click="handleAddItem" id="primaryBtnAdd">新增</d-button> -->

    <d-drawer class="card-edit-drawer" v-model="visible" :width="600" style="padding: 20px;">
      <div class="title">{{ visibleType === 'add' ? "新增" : "编辑" }}
        <span class="tips">编辑或新增的用例，需要【保存】持久化后才能支持数据归档</span>
      </div>
      <d-form ref="formRef" class="edit-form" :data="formModel">
        <d-form-item field="name" label="用例名称" :rules="nameRules">
          <d-input v-model="formModel.name" placeholder="请输入用例名称（长度限制：1-760字符）" />
        </d-form-item>
        <d-form-item field="number" label="用例编号" :rules="numberRules">
          <d-input v-model="formModel.number" placeholder="请输入用例编号（长度限制：1-500字符）" />
        </d-form-item>
        <d-form-item field="priority" label="用例等级">
          <d-select v-model="formModel.priority" :options="priorityOptions" placeholder="请选择用例等级"></d-select>
        </d-form-item>
        <d-form-item v-if="isCidaApp" field="type" label="测试类型">
          <d-select v-model="formModel.type" :options="testTypeOptions" placeholder="请选择测试类型（可选）" allow-clear></d-select>
        </d-form-item>
        <d-form-item field="pre" label="预置条件" class="pre-condition">
          <d-textarea :rows="4" style="display: block;" v-model="formModel.pre" resize="vertical" placeholder="请输入预置条件" />
        </d-form-item>
        <d-form-item field="test_step" label="测试步骤" class="pre-condition">
          <d-textarea :rows="4" style="display: block;" v-model="formModel.test_step" resize="vertical" placeholder="请输入测试步骤" />
        </d-form-item>
        <d-form-item field="expect_output" label="预期结果" class="pre-condition">
          <d-textarea :rows="4" style="display: block;" v-model="formModel.expect_output" resize="vertical" placeholder="请输入预期结果" />
        </d-form-item>
      </d-form>
      <div class="form-demo-form-operation">
        <d-button @click="visible = false">取消</d-button>
        <d-button style="margin-left: 8px;" @click="handleConfirm" variant="solid" :disabled="!isFormValid">确认</d-button>
      </div>
    </d-drawer>
    <ProjectDirSelectDialog v-model="selectDirVisible" :initial-path="projectDir" :show-files="false" @confirm="handleProjectDirConfirm" />
    <ArchiveTmssDialog
      v-model="archiveTmssVisible"
      :userInfo="userInfo"
      :data="props.data"
      :session="props.session"
      :platform="props.data?.platform"
      :cloudTestConfig="props.data?.cloudTestConfig"
      :projectId="props.data?.project_id"
      :selectData="selectData"
      @confirm="handleArchiveTmssConfirm"
    />
    <CidaExecDialog v-model="cidaExecVisible" :currentData="currentData" :projectId="props.data?.cidaProjectConfig?.projectId" :notArchived="!currentData?.tmssArchivedStatus" @execute="handleCaseExecute" />
    <CloudTestExecDialog v-model="cloudTestExecVisible" :currentData="currentData" :projectId="props.data.cidaProjectConfig?.projectId" :cloudTestConfig="props.data?.cloudTestConfig" :notArchived="!currentData?.tmssArchivedStatus" @execute="handleCaseExecute" />
  </div>
</template>
<script setup lang="ts">
import { ref, computed, watch, getCurrentInstance, nextTick, h, type Ref } from 'vue';
import { testCaseConfig } from "../../../promptConfig";
import { mindmapCreateOrUpdateByAi, mindmapUpload, createTask, openIde, queryRequirementById, apiLoading  } from '@/service/api'
import ArchiveTmssDialog from './archiveTmssDialog.vue'
import ProjectDirSelectDialog from './projectDirSelectDialog.vue'
import CidaExecDialog from './cidaExecDialog.vue'
import CloudTestExecDialog from './cloudTestExecDialog.vue'
import { UserStore } from "@/stores/user";
import { NORMAL_RANK_MAPPING, testTypeMapping } from './archive_testcase.js'
import { buildTestCaseFillResultParams, type TestCaseFillContext } from './composables/useCaseExecLogic'

const props = defineProps({
  requirementList:{
    type: Object,
    required: true
  },
  data: {
    type: Object,
    required: true
  },
  originData: {
    type: Object,
    required: true
  },
  session: {
    type: Object,
    required: true
  },
  userInfo: {
    type: Object,
    required: true
  }

})
const addReqUrlParams = (url, data) => {
  if(!url){
    return '';
  }

  let newUrl = url;
  if(data.treeType === 'reqTree'){
    newUrl  = `${url}&reqId=${data.requirement_number}&domainId=${data.cloudTestConfig?.reqSpaceId}`;
  } else if(data.treeType === 'taskTree'){
    const taskId = data.req_id.split('_')[1] || '';
    newUrl  = `${url}&testDesignTaskId=${taskId}&testDesignTreeType=${data.cloudTestConfig?.taskTreeType}`;
  }

  return newUrl;
}
const currentItem = ref('')
const currentData = ref<any>({});
const handleChangeItem = (item) => {
  if (item.itemType === 'node') {
    item.isShow = !item.isShow;
  } else {
    currentItem.value = item.number;
    currentData.value = item;
  }
}
const linkUrl = ref('');
const projectDir = ref('');
watch(() => props.data, () => {
  console.log("props.data", props.data);

  if (props.data?.test_point_list?.[0]) {
    props.data.test_point_list[0].isShow = true
    currentItem.value = props.data?.test_point_list?.[0]?.test_case_list?.[0]?.number || ''
    currentData.value = props.data?.test_point_list?.[0]?.test_case_list?.[0] || {};
  }
  (props.data?.test_point_list || []).forEach(ee => {
    ee.test_case_list.forEach(dd => {
      dd.isCheck = true;
    })
  })
  linkUrl.value = addReqUrlParams(props.data?.htsmLinkUrl, props.data);
  projectDir.value = localStorage.getItem('testAgent-project-dir') || '';
}, { immediate: true })
const formRef = ref(null)
const visible = ref(false)
const visibleType = ref('add')
const formModel = ref<any>({})
const currentParent = ref<any>({})
const selectDirVisible = ref(false)
const priorityOptions = Object.keys(NORMAL_RANK_MAPPING);
const defaultPriority = priorityOptions[2];
const testTypeOptions = Object.keys(testTypeMapping);

const nameRules = [
  { required: true, message: '用例名称不能为空！', trigger: 'blur' },
  {
    validator: (rule, value) => {
      const trimmedValue = value?.trim() || ''
      if (!trimmedValue) {
        return false
      }
      if (trimmedValue.length > 760) {
        return false
      }
      return true
    },
    message: '用例名称长度必须在1-760字符之间！',
    trigger: 'blur'
  }
]

const numberRules = [
  { required: true, message: '用例编号不能为空！', trigger: 'blur' },
  {
    validator: (rule, value) => {
      const trimmedValue = value?.trim() || ''
      if (!trimmedValue) {
        return false
      }
      if (trimmedValue.length > 500) {
        return false
      }
      return true
    },
    message: '用例编号长度必须在1-500字符之间！',
    trigger: 'blur'
  }
]

const isFormValid = computed(() => {
  const trimmedName = (formModel.value?.name || '').trim()
  const trimmedNumber = (formModel.value?.number || '').trim()
  
  if (!trimmedName || trimmedName.length > 760) {
    return false
  }
  
  if (!trimmedNumber || trimmedNumber.length > 500) {
    return false
  }
  
  return true
})

const projectName: any = computed(() => {
  return projectDir.value.replace(/^.*?\\/, '');
})

const handleAddTestSpot = (item) => {
  visibleType.value = 'add'
  visible.value = true
  formModel.value = {
    name: '',
    number: '',
    priority: defaultPriority,
    type: '',
    pre: '',
    test_step: '',
    expect_output: ''
  }
  currentParent.value = item
}

const handleOpenEditTestSpot = (item) => {
  visibleType.value = 'edit'
  visible.value = true
  const editData = JSON.parse(JSON.stringify(item))
  formModel.value = {
    name: editData.name || '',
    number: editData.number || '',
    priority: editData.priority || defaultPriority,
    type: editData.type || '',
    pre: editData.pre || '',
    test_step: editData.test_step || '',
    expect_output: editData.expect_output || ''
  }
}

const handleAddItem = () => {
  visibleType.value = 'add'
  visible.value = true
  formModel.value = {}
}
const handleConfirm = () => {
  formRef.value.validate((isValid, invalidFields) => {
    if (isValid) {
      const trimmedName = (formModel.value?.name || '').trim()
      const trimmedNumber = (formModel.value?.number || '').trim()
      
      if (!trimmedName) {
        proxy.$notificationService.open({
          content: '用例名称不能为空！',
          duration: 3000,
          type: 'error',
        });
        return;
      }
      
      if (trimmedName.length > 760) {
        proxy.$notificationService.open({
          content: '用例名称长度不能超过760字符！',
          duration: 3000,
          type: 'error',
        });
        return;
      }
      
      if (!trimmedNumber) {
        proxy.$notificationService.open({
          content: '用例编号不能为空！',
          duration: 3000,
          type: 'error',
        });
        return;
      }
      
      if (trimmedNumber.length > 500) {
        proxy.$notificationService.open({
          content: '用例编号长度不能超过500字符！',
          duration: 3000,
          type: 'error',
        });
        return;
      }
      
      const formData: any = {
        name: trimmedName,
        number: trimmedNumber,
        priority: formModel.value?.priority || defaultPriority,
        type: formModel.value?.type || '',
        pre: formModel.value?.pre || '',
        test_step: formModel.value?.test_step || '',
        expect_output: formModel.value?.expect_output || ''
      }
      
      if (visibleType.value === 'add') {
        if (!formData.uuid) {
          formData.uuid = crypto.randomUUID();
        }
        if (currentParent.value) {
          currentParent.value.test_case_list.unshift(JSON.parse(JSON.stringify(formData)))
          currentData.value = currentParent.value.test_case_list[0];
        }
        currentItem.value = formModel.value?.number
        visible.value = false
      } else {
        if (currentData.value) {
          currentData.value.name = formModel.value?.name
          currentData.value.type = formModel.value?.type
          currentData.value.priority = formModel.value?.priority
          currentData.value.pre = formModel.value?.pre;
          currentData.value.test_step = formModel.value?.test_step;
          currentData.value.expect_output = formModel.value?.expect_output;
          currentData.value.number = formModel.value?.number
          visible.value = false
          currentItem.value = formModel.value?.number

        }
      }
      nextTick(() => {
        isEditCaseFn()
      })
    }

  });


}
const handleDelete = (arr, index) => {
  proxy.$modalService
    .open({
      // title: '确定删除',
      content: '确定删除该用例？',
      isDraggable: true,
      onConfirm(close) {
        return new Promise(resolve => {
          setTimeout(() => resolve(0), 500);
        });
      },
    })
    .then(close => {
      (arr || []).splice(index, 1)
      nextTick(() => {
        isEditCaseFn()
      })
    })
    .catch(e => console.log(e));
}
const redoCount = computed(() => {
  let res = 0;
  (props.data?.test_point_list || []).forEach(ee => {
    ee.test_case_list.forEach(dd => {
      if (dd.isCheck) {
        res += 1
      }
    })
  })
  return res;
})

const selectData = computed(() => {
  const tempData = JSON.parse(JSON.stringify(props.data?.test_point_list || []))
  const currentDataJson = JSON.parse(JSON.stringify(tempData.filter(ee => {
    ee.test_case_list = ee.test_case_list.filter(dd => dd.isCheck).map(dd => ({
      ...dd,
      pre: dd.pre,
      test_step: dd.test_step,
      expect_output: dd.expect_output,
    }))
    return ee.test_case_list.some(dd => dd.isCheck)
  })))
  return currentDataJson;
})

const emits = defineEmits(['sendMessageToParent'])
// 重新生成卡片
const handleReDoCard = () => {
  const tempData = JSON.parse(JSON.stringify(props.data.test_point_list))
  const currentDataJson = JSON.parse(JSON.stringify(tempData.filter(ee => {
    ee.test_case_list = ee.test_case_list.filter(dd => dd.isCheck).map(dd => ({
      ...dd,
      pre: dd.pre,
      test_step: dd.test_step,
      expect_output: dd.expect_output,
    }))
    return ee.test_case_list.some(dd => dd.isCheck)
  })))

  const sendData = {
    type: 'chat',
    data: currentDataJson,
    prompt: testCaseConfig.regenerate(redoCount.value)
  }
  console.log(sendData);


  emits('sendMessageToParent', sendData)

}

const filePathRef = ref(null)
const isCopied = ref(false)
const { proxy } = getCurrentInstance()
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.data?.saved_file_path)
    proxy.$notificationService.open({
      content: '文件路径已复制到剪切板！',
      duration: 3000,
      type: 'success',
    });
    
  } catch (err) {
    console.error('复制失败:', err)

    try {
      document.body.appendChild(props.data?.saved_file_path)
      proxy.$notificationService.open({
        content: '文件路径已复制到剪切板！',
        duration: 3000,
        type: 'success',
      });
    } catch {
      proxy.$notificationService.open({
        content: '复制失败，请手动复制!',
        duration: 3000,
        type: 'error',
      });
    }
  }
}
const isEdit = ref(false)
const isEditCaseFn = () => {
  const currentDataJson = JSON.parse(JSON.stringify(props.data))
  currentDataJson.test_point_list = (currentDataJson.test_point_list || [])
  if (JSON.stringify(currentDataJson) === JSON.stringify(props.originData)) {
    isEdit.value = false
  } else {
    isEdit.value = true
  }
}

const userStore = UserStore();

const handleSaveCase = () => {
  const data = userStore.eventData;
  const requirementList = JSON.parse(JSON.stringify(props.requirementList));
  
  // 保存数据
  const temp = { ...data.elicition, data: requirementList, cardId: data.cardId, state: data.status };
  const elicition = JSON.parse(JSON.stringify(temp));
  console.log('send elicition', elicition);
  const sendData = {
    prompt: '刷新卡片',
    data: { elicition },
    action: 'card-save',
    type: 'chat',
  };
  emits('sendMessageToParent', sendData);
  isEdit.value = false;
};

function classifyByType(data) {
  return data.reduce((acc, item) => {
    const typeName = item.type;
    if (!acc[typeName]) {
      acc[typeName] = {
        text: typeName,
        children: []
      };
    }
    let tempItem = JSON.parse(JSON.stringify(item))
    delete tempItem.type
    acc[typeName].children.push(tempItem);
    return acc;
  }, {});
}

// 归档
const extractedLevel = (testCaseLevel) => {
  if (!testCaseLevel) {
    return 1;
  }
  // 使用正则表达式匹配数字
  const match = testCaseLevel.match(/\d+/);

  // 如果找到数字则转换为数字类型，否则返回1
  return match ? parseInt(match[0], 10) : 1;
};

const appCode = import.meta.env.VITE_HTSM_CODE;
const handlelinkTo = () => {
  window.open(linkUrl.value, '_blank');
}
const arChiveLoading = ref(false)
const archiveTmssVisible = ref(false)

const handleArchiveTmss = () => {
  archiveTmssVisible.value = true
}

const ideaAction = {
  idea: {
    registerPath: 'HKEY_CURRENT_USER\\Software\\Classes\\idea\\shell\\open\\command'
  },
  pycharm: {
    registerPath: 'HKEY_CURRENT_USER\\Software\\Classes\\pycharm\\shell\\open\\command'
  },
  vscodehuawei: {
    registerPath: 'HKEY_CURRENT_USER\\Software\\Classes\\vscodehuawei\\shell\\open\\command'
  }
}

const handleOpenIDE = (ideType) => {
  const storedProjectDir = localStorage.getItem('testAgent-project-dir') || '';
  
  if (!storedProjectDir) {
    selectDirVisible.value = true;
    return;
  }
  
  projectDir.value = storedProjectDir;
  executeOpenIDE(ideType, storedProjectDir);
}

const handleEditProjectDir = () => {
  selectDirVisible.value = true;
}

const handleProjectDirConfirm = (dirPath: string) => {
  projectDir.value = dirPath;
}

// 通过调用后台接口打开IDE
const executeOpenIDE = async (ideType, dirPath) => {
  const ideName = ideType.toUpperCase();
  try {
    const params = {
      path: dirPath,
      reg_str: ideaAction[ideType]?.registerPath
    }
    const res = await openIde(params);
    if(!res?.data?.success){
      let msg = res?.data?.message;
      
      if (msg && msg.includes('注册表未找到')) {
        msg = '该IDE未安装TestAgent插件';
      }

      proxy.$notificationService.open({
        content: `${ideName} 打开失败: ${msg}`,
        duration: 5000,
        type: 'error',
      });
    }
  } catch (e) {
    proxy.$notificationService.open({
      content: `${ideName} 打开失败`,
      duration: 3000,
      type: 'error',
    });
  }
}

/**
 * 获取归档需要的reqId
 * 在cloudTest且reqType='RequirementIone'时，需要查询origin_req_ione_id并拼接req_id
 * 否则直接返回props.data?.req_id
 */
const getReqId = async () => {
  if (props.data.platform === 'cloudtest' && props.data.reqType === 'RequirementIone' && props.data.treeType === 'reqTree') {
    try {
      const res = await queryRequirementById(props.data.requirement_id);
      if (res.data?.code === 200 && res.data?.data?.result?.length > 0) {
        const integratedSystemId = res.data.data.result[0].integrated_system_id;
        if (integratedSystemId) {
          const originReqIoneId = integratedSystemId;
          const serviceId = props.data?.cloudTestConfig?.serviceId || '';
          return `${serviceId}_${originReqIoneId}`;
        }
      }
    } catch (error) {
      console.error('查询需求详情失败:', error);
    }
  }
  return props.data?.req_id || '';
};

// 归档至测试设计脑图
const handleArchive = async () => {
  if(props.data.treeType === 'reqTree' && props.data.platform === 'cloudtest') {
    const reqId = await getReqId();
    const params = {
      reqId: reqId,
      projectId: props.data?.project_id || ''
    };
    archiveHtsm(params);
  } else if(props.data.treeType === 'reqTree' && props.data.platform === 'cida') { // CIDA
    // 按需求归档脑图需要先创CBTask任务（绑定需求）->再归档脑图
    createHtsmTask((taskId) => {
        const params = {
          reqId: taskId || '',
          projectId: props.data?.project_id || ''
        };
        archiveHtsm(params);
      });
  } else {
    // 从htsm进入
    const params = {
        reqId: props.data?.req_id || '',
        projectId: props.data?.project_id || ''
      };
      archiveHtsm(params);
  }
}

// 创建CBTask任务
const createHtsmTask = (callback) => {
  const param = {
    taskName: props.data.requirement_number,
    reqNo: props.data.requirement_number,
    reqId: props.data.req_id,
    userId: props.data.user_id,
    pduId: props.data.product_id,
    pid: props.data.requirement_number,
  }
  createTask(props.data.project_id, param).then(res => {
    if (res.status === 200 && res.data?.result == 'success') {
      let fields = res.data?.data;
      if (fields?.length) {
        callback(fields[0].instanceId);
      }
    } else {
      console.log("create task fail", res);
    }
  });
}

const getTestMindUpdateMode = () => {
  // 是否基于已创建的脑图归档
  const isCreatedTestMind = props.data.platform === 'cloudtest' ? props.data.cloudTestConfig?.isCreatedTestMind : props.data.cidaProjectConfig?.isCreatedTestMind;
  return isCreatedTestMind ? 'insert' : 'replace'; // 已有脑图进行插入处理，否则覆盖
}

// 归档脑图
const archiveHtsm = (params) => {
  if (!params.reqId || !params.projectId) {
    proxy.$notificationService.open({
      content: '需求Id或projectId不能为空！',
      duration: 3000,
      type: 'error',
    });
    return;
  }

  const tempList = (props.data?.test_point_list || []).map(ee => {
    const tempRes = {
      type: ee.type,
      text: ee.name,
      testPoint: "Y",
      generatedBy: "Y",
      testcases: ee.test_case_list.map(dd => ({
        "caseName": dd.name,
        "caseNum": dd.number,
        "caseDesignDesc": "",
        "testCaseLevel": extractedLevel(dd.priority),
        "prerequisite": dd.pre,
        "testProcedure": dd.test_step,
        "expectedResults": dd.expect_output,
        testType: '3',
      }))
    }
    return tempRes;
  })
  // 需要加一层分类
  const result = Object.values(classifyByType(tempList));

  const root = {
    text: "测试设计",
    children: [
      {
        text: props.data?.title || '',
        children: result
      }
    ]
  }
  const requestParams = {
    root,
    req_id: params.reqId,
    project_id: params.projectId,
    session_id: props.session?.id ? String(props.session?.id) : '',
    tool_type: props.data?.platform === 'cloudtest' ? 'CloudTest' : 'CIDA',
    ...getReqParam(),
    update_mode: getTestMindUpdateMode()
  }
  arChiveLoading.value = true

  mindmapCreateOrUpdateByAi(requestParams, props.userInfo?.id).then(resp => {
    const res = resp.data
    if (res.status === 'success') {
      proxy.$notificationService.open({
        content: res.message || '操作成功！',
        duration: 3000,
        type: 'success',
      });
      const htsmUrl = props.data?.platform === 'cloudtest' ? getCloudTestMindMapUrl() : getCidaMindMapUrl();
      linkUrl.value = htsmUrl;
      saveCardData();
      uploadFile(res);
    } else {
      proxy.$notificationService.open({
        content: (res.message || res.error) || '操作失败！',
        duration: 3000,
        type: 'error',
      });
    }
  }).catch(() => {
    proxy.$notificationService.open({
      content: '操作失败！',
      duration: 3000,
      type: 'error',
    });
  }).finally(() => {
    arChiveLoading.value = false
  })
}

const getReqParam = () => {
  let ids = [];
  let numbers = [];
  let types = [];
  try {
    if (props.data?.treeType !== 'reqTree') {
      // 任务的情况
      props.data?.req_origin_info?.forEach((req) => {
        ids.push(req.id);
        numbers.push(req.number);
        types.push(props.data?.reqType);
      });
    } else {
      ids = [props.data?.requirement_id];
      numbers = [props.data?.requirement_number];
      types = [props.data?.reqType];
    }
  } catch (error) { }
  return {
    requirement_req_id: ids.filter(Boolean).join(','),
    requirement_req_num: numbers.filter(Boolean).join(','),
    requirement_req_system: types.filter(Boolean).join(','),
  };
};

const uploadFile = (res: any) => {
  let resData = res.result || {}
  const content = props.data?.spec || '';
  const blob = new Blob([content], { type: 'text/markdown' });
  const file = new File([blob], 'spec.md', { type: 'text/markdown' });
  let uploadParms = {
    mindmapId: resData.mindmapId,
    parentId: resData.root?.id,
    nodeId: resData.root?.children?.[0]?.id,
    app: 'CIDA',
    file: file,
    type: 'doc',
  }
  mindmapUpload(uploadParms, { userId: props.userInfo?.id, projectId: props.data.project_id }).then(resp2 => {
    let res2 = resp2.data
    if (res2.status === 'success') {
      proxy.$notificationService.open({
        content: res2.message || '上传成功！',
        duration: 3000,
        type: 'success',
      });
    }
  })
};

const saveCardData = () => {
  // 保存数据
  props.data.htsmLinkUrl = linkUrl.value;
  handleSaveCase();
};

// 归档至测试用例管理
const handleArchiveTmssConfirm = (node) => {
  if(node?.successCaseItems?.length) {
    const list = [];
    props.data.test_point_list.forEach((item) => {
      if (item.test_case_list?.length) {
        item.test_case_list.forEach((caseItem) => {
          list.push(caseItem);
        });
      }
    });
    // 回填用例uri url tmssArchivedStatus
    node.successCaseItems.forEach(successCaseItem => {
      const caseItem = list.find(caseItem => caseItem.number === successCaseItem.number && caseItem.uuid === successCaseItem.uuid);
      if (caseItem) {
        caseItem.uri = successCaseItem.uri;
        caseItem.url = successCaseItem.url;
        caseItem.tmssArchivedStatus = successCaseItem.tmssArchivedStatus;
      }
    });
    handleSaveCase();
  }
}

const cidaExecVisible = ref(false)
const cloudTestExecVisible = ref(false)

/**
 * 用例执行入口
 * 根据当前平台分发到不同的执行弹窗
 * cida场景打开CidaExecDialog，cloudTest场景打开CloudTestExecDialog
 */
const useCaseAnalysis = () => {
  const openDialog = (visibleRef: Ref<boolean>) => {
    visibleRef.value = false
    nextTick(() => { visibleRef.value = true })
  }

  if (props.data.platform === 'cida') {
    openDialog(cidaExecVisible)
  } else if (props.data.platform === 'cloudtest') {
    openDialog(cloudTestExecVisible)
  }
}

/**
 * 处理用例执行事件
 * 由cidaExecDialog或cloudTestExecDialog在导入/确认后触发
 * @param caseData - 用例数据
 */
const handleCaseExecute = (caseData: any, fillContext: TestCaseFillContext) => {
  console.log('fillContext: ', fillContext);
  const isTmss = props.data.platform === 'cida';
  const projectId = props.data?.project_id;
  const serviceIdOrProjectId = isTmss ? (projectId || '') : (props.data?.cloudTestConfig?.serviceId || '');
  const testCaseFillResultParams = buildTestCaseFillResultParams(isTmss, serviceIdOrProjectId, fillContext);
  console.log('testCaseFillResultParams: ', testCaseFillResultParams);
  const caseItem: Record<string, any> = {
    name: currentData.value.name,
    number: currentData.value.number,
    Preparation: currentData.value.pre || '',
    TestStep: currentData.value.test_step || '',
    ExpectOutput: currentData.value.expect_output || '',
  };
  if (currentData.value?.tmssArchivedStatus) {
    caseItem.testCaseFillResultParams = testCaseFillResultParams;
  }
  const caseList = [caseItem];
  console.log('currentData.value:');
  console.log(currentData.value);
  console.log('caseList:');
  console.log(caseList);
  emits('sendMessageToParent', {
    type: 'chat',
    action: 'resolve-testcase',
    data: {
      caseList: caseList,
    },
    prompt: `请使用"rewrite-testcase-steps"skill，对以下测试用例的测试用例步骤进行改写：
      严格返回以下json格式，禁止多返回多余内容，所有的key和结构必须与以下下格式一致：
      {
        "status": "success",
        "pre_steps": [
          "系统已启动并运行正常，通过ping命令检查系统响应",
          "测试用户账号已创建且具备登录权限，通过用户管理界面验证"
        ],
        "steps": [
          {
            "origin_steps": "在登录页面，输入用户名和密码，点击登录按钮",
            "min_steps": [
              "在登录页面，输入用户名",
              "在密码输入框，输入密码",
              "点击登录按钮"
            ],
            "expect": "预期结果1. 登录成功，页面跳转到首页，URL为目标地址，通过URL检查和页面内容检查验证"
          }
        ]
      }

      用例名称：${currentData.value.name}
      用例编号：${currentData.value.number}
      预置条件：${currentData.value.pre}
      测试用例步骤：${currentData.value.test_step}
      预期结果 ${currentData.value.expect_output}`
  })
}

const getCidaMindMapUrl = () => {
  let path = props.data?.requirement_id;
  let taskType = 'newReqTree';
  if (props.data?.treeType !== 'reqTree') {
    // treeType=reqTree代表是需求树选择进入，否则从htsm脑图的AI新建触发
    path = props.data?.req_id;
    taskType = 'task';
  }
  return `${import.meta.env.VITE_CIDA_URL}/deskui/project/projectDetail/${
    props.data.project_id
  }/123456/SDV?appCode=${appCode}&path=${path}&taskType=${taskType}`;
};

const getCloudTestMindMapUrl = () => {
  if (!props.data?.cloudTestConfig) {
    return '';
  }
  const domain = import.meta.env.VITE_CLOUDTEST_URL;
  const { groupId, serviceId, branchUri, iterationUri } = props.data.cloudTestConfig;
  let url = `${domain}/cloudtest/project/${groupId}/serviceDetail/requirement?serviceId=${serviceId}&branchUri=${branchUri}&iterationUri=${iterationUri}`;
  url = addReqUrlParams(url, props.data);
  return url;
};

const getCaseTotal: any = computed(() => {
  let count = 0;
  (props.data?.test_point_list || []).forEach(ee => {
    ee.test_case_list.forEach(ii => {
      count++;
    })
  })
  return count;
});

const getTpTotal: any = computed(() => {
  return props.data?.test_point_list?.length ?? 0;
});

const isCidaApp: any = computed(() => {
  return props.data?.platform === 'cida';
});
</script>
<style lang="scss" scoped>
.testSpot {
  width: 100%;
  height: 100%;
  position: relative;

  .operation-button-box {

    .dv-button {
      margin-left: 8px;
    }
  }

  .title-header {

    padding-bottom: 20px;
    border-bottom: 2px solid #f5f7fa;

    .title-detail {
      font-size: 18px;
      font-weight: bold;
    }

    .dv-link {
      display: inline-block;
      white-space: nowrap;
      /* 禁止换行 */
      overflow: hidden;
      /* 隐藏溢出内容 */
      text-overflow: ellipsis;
      /* 显示省略符号 */
      width: calc(100% - 80px);
      /* 必须设置宽度（或max-width）*/
    }

    ::v-deep(.dv-alert__content) {
      display: flex;
      align-items: center;
      width: calc(100% - 24px);
    }

    .test-count {
      margin-top: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .header-left {
        display: flex;
        align-items: center;
        font-size: 12px;
      }

      .count-info {
        font-size: 12px;
        color: #999;
      }

      .project-dir {
        margin-left: 12px;
        display: inline-flex;
        align-items: center;
        
        .project-name {
          max-width: 150px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          display: inline-block;
        }
      }
    }
  }

  .test-spot-list {
    display: flex;
    height: calc(100% - 88px);

    .left-lsit {
      width: 35%;
      height: 100%;
      overflow-y: auto;
      border-right: 1px solid #f5f7fa;

      .list-item {
        cursor: pointer;
        // display: flex;
        align-items: center;
        padding: 12px 16px 12px 4px;
        border-bottom: 1px solid #f5f7fa;


        .item-title-content {
          display: flex;
          align-items: center;
          padding-bottom: 12px;

          .item-icon {
            display: inline-block;
            border: 6px solid transparent;
            border-left: 12px solid #ccc;
            width: 0;
            height: 0;
            margin-right: 8px;
            transform: rotate(0);
            transition: transform 0.3s ease;
          }

          .item-title {
            display: inline-block;
            color: #409eff;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
            flex: 1;
          }
        }


      }

      .list-item-show {
        .item-title-content {
          .item-icon {
            border-left: 12px solid #409eff;
            transform: rotate(90deg) translate(4px);
            transition: transform 0.3s ease;
          }

        }
      }

      .list-item-select {
        background: #f5f7fa;
      }

      .children-item {
        padding: 12px 0 12px 4px;
        border-top: 1px solid #f5f7fa;
        display: flex;
        align-items: center;
        margin-left: 22px;

        .item-title {
          display: inline-block;
          color: #aaa;
          white-space: nowrap;
          text-overflow: ellipsis;
          overflow: hidden;
          flex: 1;
        }

        .child-classFy {
          display: inline-block;
          padding: 4px 8px;
          border-radius: 4px;
          background-color: #f5f7fa;
          color: #aaa;
          margin-left: 8px;
          font-size: 12px;
        }
      }

      .current-child {
        background: #f5f7fa;
      }

      .P0,
      .P1 {
        .item-title {
          color: #e6a23c;
        }

        .child-classFy {
          background-color: #fdf6ec;
          color: #e6a23c;
        }

      }
    }

    .right-content {
      flex: 1;
      // display: flex;
      // flex-direction: column;
    }

    .right-detail {
      margin: 20px 0 0 20px;
      border: 1px solid #f5f7fa;
      border-radius: 8px;
      // height: min-content;
      flex: 1;
      height: calc(100% - 20px);
      // min-height: 0;

      .right-header {
        padding: 20px;
        background: #f5f7fa;

        .detail-title {
          font-weight: bold;
          display: -webkit-inline-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 3;
          line-clamp: 3;
          overflow: hidden;
          word-break: break-all;
        }

        .detail-header-info {
          display: flex;
          align-items: center;
          margin-top: 12px;

          span {
            font-size: 12px;
            flex-shrink: 0;

            .info-title {
              color: #aaa;
            }

            .info-classFy {
              display: inline-block;
              border: 1px solid #f56c6c;
              color: #f56c6c;
              background-color: #fef0f0;
              padding: 2px 4px;
              border-radius: 4px;

            }

            .info-type {
              display: inline-block;
              color: #409eff;
              background-color: #ecf5ff;
              border: 1px solid #409eff;
              padding: 2px 4px;
              border-radius: 4px;
            }
          }

          .number-container {
            flex-shrink: 1;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 3;
            line-clamp: 3;
            overflow: hidden;
            word-break: break-all;
          }
        }
      }

      .right-container {
        padding: 20px;
        height: calc(100% - 95px);
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        gap: 12px;

        .contain-name {
          border-left: 2px solid #409eff;
          padding-left: 12px;
          font-weight: bold;
          margin-bottom: 8px;
          flex-shrink: 0;
        }

        .contain-value {
          // background: #f5f7fa;
          // border-left: 2px solid #409eff;
          // border-radius: 4px;
          // padding: 12px;
          margin: 16px 0 12px 0;
          color: #999;
          font-size: 14px;
          word-break: break-all;

          .value-icon {
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #aaa;
            margin-right: 8px;
          }

          .step-icon {
            display: inline-block;
            width: 20px;
            height: 20px;
            text-align: center;
            line-height: 20px;
            border-radius: 50%;
            background-color: #409eff;
            margin-right: 8px;
            color: #ecf5ff;
          }
        }

        .contain-value-text {
          margin: 8px 0;
          color: #999;
          font-size: 14px;
          word-break: break-all;
          white-space: pre-wrap;
          line-height: 1.6;
        }

        .content-section {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
          overflow: hidden;

          .section-content {
            flex: 1;
            overflow-y: auto;
            min-height: 0;
          }
        }
      }
    }
  }

  .test-spot-list-show-link {
    height: calc(100% - 145px);
  }


}
</style>
<style lang="scss">
.card-edit-drawer {
  .edit-form {
    height: calc(100% - 100px);
    overflow: auto;

  }

  .form-demo-form-operation {
    margin-top: 20px;
    margin-left: 115px;
  }

  .title {
    font-weight: bold;
  }

  .edit-form {
    margin-top: 20px;
  }

  .pre-condition {
    .dv-form__control-container--horizontal {
      display: block;
    }

    .step-item {
      margin-bottom: 8px;
      display: flex;
      align-items: center;

      .operation-icon {
        width: 60px;
      }
    }

    .icon-aom-minussquare {
      margin-left: 4px;
      color: #c7000b;
      cursor: pointer;
    }

    .icon-aom-plussquare {
      margin-left: 8px;
      color: #5e7ce0;
      cursor: pointer;
    }
  }

}

.testSpot-operation-button {

  // padding: 12px;
  .operation-item {
    padding: 8px 12px;
    color: #333;
    cursor: pointer;

    &:hover {
      background-color: #f5f7fa;
    }

  }
}

.ide-dropdown-menu {
  .ide-item {
    padding: 8px 12px;
    color: #333;
    cursor: pointer;

    &:hover {
      background-color: #f5f7fa;
    }
  }
}

.title > .tips {
  font-size: 14px;
  margin-left: 30%;
  color: orange;
}

.tips-height {
  max-height: 300px;
  overflow-y: auto;
}
</style>

