<template>
  <d-modal v-model="visible" title="用例归档" width="64%" :before-close="beforeClose">
    <div class="archive-dialog-content">
      <div class="archive-section case-list-section">
        <div class="section-header">
          <h4 class="section-title">用例列表</h4>
          <span class="case-count">({{ allCaseItems?.length  }})</span>
          <div class="select-all">
            <input
                type="checkbox"
                @change="toggleSelectAll($event)"
            />
            <span class="select-all-title">全选</span>
          </div>
        </div>
        <div class="case-list-wrapper">
          <div v-if="allCaseItems?.length">
            <d-tooltip
              v-for="(item, index) in allCaseItems"
              :key="index"
              :content="caseDuplicateInfo.get(index)?.disabled ? caseDuplicateInfo.get(index)?.reason : ''"
              position="top"
            >
              <div
                class="case-item"
                :class="{ 'is-selected': item.checked, 'is-disabled': caseDuplicateInfo.get(index)?.disabled }"
              >
                <input
                  v-if="!caseDuplicateInfo.get(index)?.disabled"
                  type="checkbox"
                  :checked="item.checked"
                  @change="toggleSelect($event, item)"
                />
                <i
                  v-else
                  class="icon icon-ban"
                ></i>
                <span class="case-index">{{ index + 1 }}</span>
                <span class="case-name" :title="item.name">{{ item.name }}</span>
                <span v-if="isItemArchived(item)" class="archived-tag">已归档</span>
              </div>
            </d-tooltip>
          </div>
          <div v-else class="empty-tip">暂无可归档用例</div>
        </div>
      </div>
      <div class="archive-divider"></div>
      <div class="archive-section tree-section">
        <div class="section-header">
          <h4 class="section-title">版本用例树</h4>
        </div>

        <!-- cloudtest: 分支和迭代下拉框 -->
        <template v-if="isCloudTestPlatform()">
          <div class="title-merge">
            <span>服务名称：</span>
            <span>{{ serviceName }}</span>
          </div>
          <div class="title-merge">
            <span class="label-text">分支:</span>
            <d-select
              class="default-select"
              v-model="currentBranch"
              :options="branchOptions"
              value-key="uri"
              filter-key="name"
              placeholder="master"
              :filter="true"
              @value-change="changeBranch"
            ></d-select>
          </div>
          <div class="title-merge">
            <span class="label-text">迭代:</span>
            <d-select
              class="default-select"
              v-model="currentIteration"
              :options="iterationOptions"
              value-key="uri"
              filter-key="name"
              placeholder="Baseline"
              :filter="true"
            ></d-select>
          </div>

          <div class="title-merge">
            <span class="label-text">阶段:</span>
            <d-select
              v-model="filterValues.stage"
              :options="filterOptions.stage"
              placeholder="请选择阶段"
              @value-change="stageChange"
              size="sm"
              clearable
            />
          </div>
          <div class="title-merge">
            <span class="label-text">类型:</span>
            <d-select
              v-model="filterValues.type"
              :options="filterOptions.type"
              placeholder="请选择类型"
              size="sm"
              clearable
            />
          </div>
          <div class="title-merge">
            <span class="label-text">测试平台:</span>
            <d-select
              v-model="filterValues.testPlatform"
              :options="filterOptions.testPlatform"
              placeholder="请选择测试平台"
              size="sm"
              clearable
            />
          </div>

          <!-- cloudtest: feature树 -->
          <div class="cloud-test-tree">
            <d-tree
              ref="cloudTestTreeRef"
              v-if="featureTreeData.length"
              :data="featureTreeData"
              @node-click="featureNodeClick"
              @lazy-load="lazyLoadCloudTestTree"
            >
              <template #content="{ nodeData }">
                <span class="custom-tree-node" :title="nodeData.label">
                  <i :class="nodeData.data?.type === 'folder' ? 'icon-folder' : 'icon-test-manager'"></i>
                  {{ nodeData.label }}
                </span>
                <!-- 隐藏元素后续开发 -->
                <span
                  v-if="!nodeData.data?.loading && !nodeData.isLeaf"
                  class=""
                  title="刷新目录"
                  @click.stop="refreshChildFeature(nodeData)"
                ></span>
              </template>
            </d-tree>
            <div v-if="!featureTreeData.length" class="empty-tip">
              <span v-if="cloudTestErrorFlag">TMSS服务暂不可用，请<span class="link" @click="initCloudTestTree">稍后重试</span></span>
              <span v-else>无数据</span>
            </div>
          </div>
        </template>

        <!-- cida: 原有TMSS树 -->
        <template v-else>
          <d-tree ref="cidaTreeRef" :data="cidaTreeData" class="tmss-tree" @lazy-load="lazyLoad" @node-click="nodeClick">
            <template #content="{ nodeData }">
              <span class="custom-tree-node" :id="nodeData.realURI">
                <i
                  :class="`${nodeData.type === 'TestCase' ? 'icon-testCase' : 'icon-common'} ${nodeData.className || ''}`"
                ></i>
                <span v-if="scrollNodeUri === nodeData.realURI" :title="nodeData.name" style="background-color: #fac20a">{{
                  nodeData.name
                }}</span>
                <span v-else :title="nodeData.name">{{ nodeData.name }}</span>
              </span>
            </template>
          </d-tree>
        </template>
      </div>
    </div>
    <template #footer>
      <d-modal-footer>
        <d-button variant="solid" :disabled="!isChecked" @click="handleConfirm" :loading="confirmLoading">确认</d-button>
        <d-button variant="solid" color="secondary" @click="handleClose">取消</d-button>
      </d-modal-footer>
    </template>
  </d-modal>

  <d-modal v-model="failedVisible" title="归档失败详情" width="800px">
    <d-data-grid
      :data="failedTableData"
      :columns="failedColumns"
      fix-header
      size="sm"
      :show-overflow-tooltip="true"
      resizable
      class="failed-table"
    ></d-data-grid>
  </d-modal>

  <d-modal v-model="duplicateVisible" title="用例编号已存在" width="700px">
    <div>
      <d-alert type="warning" :closeable="false">{{ duplicateCaseList.length }}条用例编号已存在，请修改后重新归档，如不修改，相同编号用例会覆盖</d-alert>
      <d-data-grid
        :data="duplicateCaseList"
        :columns="[
          { type: 'index', header: '序号', width: 60 },
          { field: 'name', header: '用例名称' },
          { field: 'number', header: '用例编号' }
        ]"
        fix-header
        size="sm"
        style="height: 400px"
        :show-overflow-tooltip="true"
      ></d-data-grid>
    </div>
    <template #footer>
      <d-modal-footer>
        <d-button variant="solid" @click="handleContinueArchive">继续归档</d-button>
        <d-button variant="solid" color="secondary" @click="duplicateVisible = false">取消</d-button>
      </d-modal-footer>
    </template>
  </d-modal>
</template>

<script setup lang="ts">
import { ref, getCurrentInstance, watch, computed } from 'vue';
import {
  getChildrenNode,
  getProjectInfo,
  cidaCaseArchive,
  setTmssBaseUrl,
  getCloudTestIterationByServiceId,
  getCloudTestIteration,
  queryFeatureList,
  queryChildFeatureList,
  queryCloudTestConfigByProjectId,
  getCloudTestActivityService,
  createCloudTestCase,
  getCloudTestServiceById,
  sessionRecode,
  createTcRelationByCloudTest,
  createTcRelationByCida,
  queryRmUriByNumber,
  createCaseReqRelation,
  createCloudAlmCaseReqRelation,
  createCloudTestCaseReqRelation,
  queryCaseByNumbers,
  queryCloudTestCaseByNumbers,
} from '@/service/api';
import iconType from '../utils/getTreeIcon';
import { CLOUD_TEST_TYPE, transformToCidaRequest, rankMapping } from './archive_testcase.js'
import { ARCHIVE_STATUS } from '@/service/type';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  data: {
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
  },
  projectId: {
    type: String,
    default: '',
  },
  selectData: {
    type: Array,
  },
  platform: {
    type: String,
    default: 'cida',
  },
  cloudTestConfig: {
    type: Object,
    default: () => ({}),
  },
});

const allCaseItems = ref<any[]>([]);
const caseDuplicateInfo = ref<Map<number, { disabled: boolean; reason: string }>>(new Map());

const cloudTestServiceInfo = ref();

const cloudTestTreeRef = ref();
const cidaTreeRef = ref();

const emit = defineEmits(['update:modelValue', 'confirm']);

const { proxy } = getCurrentInstance();

const visible = ref(false);

const fields = [
  'uri',
  'name',
  'rmType',
  'resourceType',
  'type',
  'Mark',
  'versionPath',
  'VersionStatus',
  'versionType',
  'parentPath',
  'spaceUri',
  'hasChildPhysicalCase',
  'ProductLine_id',
  'archiveStatus',
  'IsShareBaseline',
  'hideFeature',
  'polymorphCombinationName',
  'polymorphCombinationPath',
  'polymorphCombinationUri',
  'comment',
  'RelatedCases',
  'LastResult',
  'isFeature',
  'RelationStatus',
  'RelatedDefects',
  'AutoType',
  'physicalAutoType',
  'ExistAttachments',
  'markReason',
  'exeplatform',
  'reviewStatus',
  'lastModifier',
  'reviewOn',
];

const tmssVersions = ref([]);
const tmsstant = ref('');
const cidaTreeData = ref([]);
const currentNode = ref<any>({});
const archivedItems = ref(new Set());
const selectedSet = ref(new Set());

const hasSelectedItems = ref(false);

const failedVisible = ref(false);
const failedTableData = ref([]);

const failedColumns = [
  { type: 'index', header: '序号', width: 60 },
  { field: 'name', header: '用例名称' },
  { field: 'reason', header: '失败原因' }
];

const duplicateVisible = ref(false);
const duplicateCaseList = ref<any[]>([]);
const pendingArchiveItems = ref<any[]>([]);

// cloudtest 相关变量
const serviceName = ref('');
const branchOptions = ref([]);
const currentBranch = ref(null);
const iterationOptions = ref([]);
const currentIteration = ref(null);
const featureTreeData = ref([]);
const selectedFeatureNode = ref(null);
const cloudTestErrorFlag = ref(false);
const cloudTmssUrl = ref('');
const confirmLoading = ref(false);

// 缓存相关
const CACHE_KEY_PREFIX = 'cloudTest_archive_cache_';

const getCacheKey = (serviceId: string) => {
  return `${CACHE_KEY_PREFIX}${serviceId}`;
};

const saveCache = (serviceId: string) => {
  if (!serviceId) return;
  const cacheData = {
    branchUri: currentBranch.value?.uri,
    iterationUri: currentIteration.value?.uri,
    stage: filterValues.value.stage,
    type: filterValues.value.type,
    testPlatform: filterValues.value.testPlatform,
  };
  localStorage.setItem(getCacheKey(serviceId), JSON.stringify(cacheData));
};

const loadCache = (serviceId: string) => {
  if (!serviceId) return null;
  const cacheStr = localStorage.getItem(getCacheKey(serviceId));
  if (!cacheStr) return null;
  try {
    return JSON.parse(cacheStr);
  } catch {
    return null;
  }
};

const beforeClose = done => {
  saveCache(props.cloudTestConfig?.serviceId);
  done();
};

const isItemArchived = (item) => {
  return archivedItems.value.has(item.uuid || item.name) || item?.tmssArchivedStatus === ARCHIVE_STATUS.ARCHIVED;
};

/**
 * 全选事件触发
 *
 * @param event
 */
const toggleSelectAll = (event) => {
  if (event.currentTarget.checked) {
    allCaseItems.value.forEach((item: any, index: number) => {
      if (!caseDuplicateInfo.value.get(index)?.disabled) {
        selectedSet.value.add(item.name);
        item.checked = true;
      }
    })
  } else {
    selectedSet.value.clear();
    allCaseItems.value.forEach((item: any) => {
      item.checked = false;
    });
  }
  hasSelectedItems.value = selectedSet.value.size > 0;
}

const toggleSelect = (event, item) => {
  item.checked = event.target.checked;
  const key = item.name;
  if (selectedSet.value.has(key)) {
    selectedSet.value.delete(key);
  } else {
    selectedSet.value.add(key);
  }
  hasSelectedItems.value = selectedSet.value.size > 0;
};

const filterValues = ref({
  stage: null,
  type: null,
  testPlatform: null,
});

const filterOptions = ref({
  stage: [],
  type: [],
  testPlatform: [],
});

const stages = [
  { value: '1', name: 'Alpha' },
  { value: '2', name: 'Beta' },
  { value: '3', name: 'Gamma' },
  { value: '4', name: 'Production' },
];
const defaultStage = stages[2];
const combinationStages = [
  { value: '5', name: 'Iota' },
  { value: '6', name: 'Kappa' },
  { value: '7', name: 'Lambda' },
];
const defaultCombinationStage = combinationStages[1];

let alphaActivity = ref([]);
let betaActivity = ref([]);
let gammaActivity = ref([]);
let prodActivity = ref([]);
let iotaActivity = ref([]);
let kappaActivity = ref([]);
let lambdaActivity = ref([]);

// ==================== CIDA 逻辑 ====================

const getTreeData = () => {
  if (!props.projectId) {
    console.log('no projectId');
    return;
  }
  getProjectInfo(props.projectId).then(res => {
    if (res.status === 200 && res.data.status === 'ok') {
      let result = { ...res.data.result };
      if (result.tmssUrl) {
        const { address, serviceName } = result.tmssUrl || {};
        const addressNum = address.match(/(?<=szvtms)\d+(?=\.tmss)/);
        let url = new URL(address);
        let tmss_base_url = url.host.replaceAll(".","_");
        setTmssBaseUrl(tmss_base_url);
        if (addressNum) {
          tmsstant.value = `TMSS_SZV${addressNum}` || serviceName;
        }
      }
      tmssVersions.value = result.tmssVersions || [];
      cidaTreeData.value = tmssVersions.value.map(item => {
        const type = item.elementName;
        const className = iconType.testCase[type] ? iconType.testCase[type](item, true) : type;
        return {
          ...item,
          type: type,
          className: className,
          isLeaf: false,
          disableCheck: true,
          realURI: item.uri,
          id: item.uri,
          label: item.name,
        };
      });
    }
  });
};

const lazyLoad = (node, callback) => {
  const uri = node.level > 1 ? node.realURI : node.uri;
  loadChildrenNodes(callback, uri, 1, 200, [], node);
};

const loadChildrenNodes = (callback, uri, pageNo, pageSize, resultList, node) => {
  let types = "Space,Product,ContainerVersion,BaselineVersion,TestVersion,TestCaseContainer,TestScene,TestItem,Feature,TestCase,PhysicalTestCase";
  let param = {
    types: types,
    fields: fields.join(","),
    pageNo,
    pageSize: 200,
    inDevVersionView: false
  }

  getChildrenNode(uri, param).then(res => {
    if (res.status === 200 && res.data.status === 'ok') {
      let resultData = res.data.result;
      let result = resultData.value.children[0].children;
      const { total } = resultData.value.children[1];

      result = result.filter(item => item.versionType === 'BaselineVersion');
      result.forEach(item => {
        item.id = item.realURI;
        item.label = item.name;
        item.isLeaf = item.type === 'TestCase';
        item.className = iconType.testCase[item.type](item);
        item.disableCheck =
          item.type === 'TestCaseContainer' ||
          ['baselineversion', 'testversion', 'nopbi_top testversion'].includes(item.className.trim().toLowerCase());
        resultList.push(item);
      });
      if (total <= pageNo * pageSize) {
        callback({
          treeItems: resultList,
          node,
        });
      } else {
        const pageNum = pageNo + 1;
        loadChildrenNodes(callback, uri, pageNum, 200, resultList, node);
      }
    } else {
      callback({
        treeItems: resultList,
        node,
      });
    }
  });
};

const nodeClick = node => {
  currentNode.value = { ...node };
};

/**
 * 获取父目录数组
 * 从当前节点向上查找，直到找到 name='Cases' 且 type='TestCaseContainer' 的节点
 * 返回从该父节点到当前节点的名称数组
 */
const getParentDirectories = (nodeId: any): string[] => {
  if (!nodeId) {
    return [];
  }
  const node = cidaTreeRef.value.treeFactory.getNode(nodeId);
  if (!node) {
    return [];
  }
  const directories: string[] = [];
  let currentNodeInPath: any = node;

  while (currentNodeInPath) {
    if (currentNodeInPath.label === 'Cases' && currentNodeInPath.type === 'TestCaseContainer') {
      break;
    }
    
    if (currentNodeInPath.label) {
      directories.unshift(currentNodeInPath.label);
    }
    
    currentNodeInPath = cidaTreeRef.value.treeFactory.getParent(currentNodeInPath);
  }

  return directories;
};

// ==================== CloudTest 逻辑 ====================

const initCloudTestTree = () => {
  const serviceId = props.cloudTestConfig?.serviceId;
  if (!serviceId) {
    currentBranch.value = null;
    return;
  }
  // 加载缓存
  const cache = loadCache(serviceId);
  if (cache?.stage?.value) {
    filterValues.value.stage = cache.stage || filterValues.value.stage;
  }
  // 获取微服务信息
  getCloudTestServiceById(props.cloudTestConfig?.serviceId).then((res) => {
    if (res?.status === 200 && res?.data?.status === 'ok') {
      cloudTestServiceInfo.value = res.data?.result;
      // 获取tmssUrl
      cloudTmssUrl.value = res.data?.result?.tmssAddress;
    }
    getCloudTestType(cache);
    getCloudTestActivity(res.data?.result, cache);
    cloudTestErrorFlag.value = false;
    const param = {
      tmssUrl: cloudTmssUrl.value,
      serviceId: serviceId,
    };
    getCloudTestIterationByServiceId(param)
      .then((res) => {
        if (res?.status === 200 && res?.data?.status === 'success') {
          const value = res?.data?.result?.value || [];
          branchOptions.value = value.map((item) => ({
            uri: item.uri,
            name: item.name,
          }));
          if (branchOptions.value.length > 0) {
            setCurrentBranch(cache);
            getIterations(currentBranch.value?.uri, cache);
            refreshFeatureTree(currentBranch.value?.uri);
          } else {
            currentBranch.value = null;
          }
        }
      })
      .catch(() => {
        cloudTestErrorFlag.value = true;
      });
  });
};

const setCurrentBranch = (cache?: any) => {
  if (!branchOptions.value?.length) {
    return;
  }
  // 1、从缓存获取分支
  let defaultBranch = cache?.branchUri
    ? branchOptions.value.find((e) => e.uri === cache.branchUri)
    : null;
  // 2、从参数获取分支
  if (!defaultBranch) {
    defaultBranch = branchOptions.value.find((e) => e.uri === props.cloudTestConfig?.branchUri);
  }
  // 3、获取master
  if (!defaultBranch) {
    defaultBranch = branchOptions.value.find((e) => e.name === 'master');
  }
  // 4、获取第一个
  if (!defaultBranch) {
    defaultBranch = branchOptions.value[0];
  }
  currentBranch.value = defaultBranch;
};

const getCloudTestType = (cache?) => {
  queryCloudTestConfigByProjectId(props?.data?.cloudTestConfig?.groupId)
    .then((res) => {
      if (res?.status === 200 && res?.data?.status === 'ok') {
        if (res?.data?.result?.length) {
          const typeConfig = res?.data?.result.find((config) => config.type === 'TestType_L2_CustomName');
          if (typeConfig) {
            handleType(JSON.parse(typeConfig.content), cache);
          }
        } else {
          handleType(cache);
        }
      }
    })
    .finally(() => {
      if (!filterOptions.value.type?.length) {
        handleType(cache);
      }
    });
};

const handleType = (list?, cache?) => {
  if (list?.length) {
    const types = list
      .filter((e) => e.enable)
      .map((e) => {
        const type = CLOUD_TEST_TYPE[e.fieldName];
        if (type?.zh) {
          type.name = type.zh;
        }
        return type;
      });
    filterOptions.value.type = [
      { name: "", value: "" },
      ...types.filter((type) => type && type.show),
    ];
  } else {
    filterOptions.value.type = [
      { name: "", value: "" },
      ...Object.values(CLOUD_TEST_TYPE).filter((e: any) => {
        if (e.zh) {
          e.name = e.zh;
        }
        return e.enable && e.show;
      }),
    ];
  }
  filterValues.value.type = cache?.type ? cache.type : filterOptions.value.type[1];
};

const getCloudTestActivity = (serviceInfo: any, cache?) => {
  getCloudTestActivityService(props?.data?.cloudTestConfig?.serviceId).then((res: any) => {
    if (res?.status === 200 && res?.data?.status === 'ok') {
      const data = res.data.result;
      serviceName.value = data.name;
      const activities = data.activities;
      alphaActivity.value = getActivities(activities, 1);
      betaActivity.value = getActivities(activities, 2);
      gammaActivity.value = getActivities(activities, 3) || [];
      prodActivity.value = getActivities(activities, 4);
      iotaActivity.value = getActivities(activities, 5);
      kappaActivity.value = getActivities(activities, 6);
      lambdaActivity.value = getActivities(activities, 7);
      // 组合服务
      if (serviceInfo?.type === 2) {
        filterOptions.value.stage = combinationStages;
        filterValues.value.stage = defaultCombinationStage;
        stageChange(filterValues.value.stage);
      } else {
        filterOptions.value.stage = stages;
        filterValues.value.stage = defaultStage;
        stageChange(filterValues.value.stage);
      }
      if (cache && cache?.stage?.value) {
        filterValues.value.stage = cache?.stage;
        stageChange(filterValues.value.stage);
        filterValues.value.testPlatform = cache?.testPlatform;
      }
    }
  });
};

const getActivities = (activities, stageId) => {
  if (!activities?.length) return [];
  stageId = String(stageId);
  const list = activities.filter(
    (e) =>
      e.stageId === stageId &&
      !["Security Test", "Service Contract Test"].includes(e.activityName)
  );
  list.unshift({
    activityName: "",
    activityId: "",
  });
  return list;
};

const activityMap = {
  1: alphaActivity,
  2: betaActivity,
  3: gammaActivity,
  4: prodActivity,
  5: iotaActivity,
  6: kappaActivity,
  7: lambdaActivity,
};

const mapActivityToOptions = (list) => (list || []).map((e) => ({
  name: e.activityName,
  value: e.activityId,
}));

const stageChange = ($event) => {
  if (!$event) {
    return;
  }
  const activity = activityMap[$event.value];
  if (activity) {
    filterOptions.value.testPlatform = mapActivityToOptions(activity.value);
    filterValues.value.testPlatform = filterOptions.value.testPlatform[0];
  }
};

const getIterations = (branchUri, cache?: any) => {
  if (!branchUri) return;
  getCloudTestIteration(branchUri).then((res) => {
    const result = (res?.data?.result?.value || []).map((it) => ({ uri: it.uri, name: it.name }));
    iterationOptions.value = [{ uri: '', name: 'Baseline' }, ...result];
    setCurrentIteration(cache);
  });
};

const setCurrentIteration = (cache?: any) => {
  if (!iterationOptions.value?.length) {
    return;
  }
  // 1、从缓存获取迭代
  let defaultIt = cache?.iterationUri
    ? iterationOptions.value.find((it) => it.uri === cache.iterationUri)
    : null;
  // 2、从参数获取迭代
  if (!defaultIt) {
    defaultIt = iterationOptions.value.find(
      (it) => it.uri === props.cloudTestConfig?.iterationUri
    );
  }
  // 3、获取第一个
  if (!defaultIt) {
    defaultIt = iterationOptions.value[0];
  }
  currentIteration.value = defaultIt;
};

const changeBranch = (item) => {
  const branchUri = item?.uri || currentBranch.value?.uri;
  if (!branchUri) return;
  currentIteration.value = null;
  getIterations(branchUri);
  refreshFeatureTree(branchUri);
  selectedFeatureNode.value = null;
};

const refreshFeatureTree = (uri) => {
  featureTreeData.value = [];
  if (!uri) return;
  const serviceId = props.cloudTestConfig?.serviceId;
  const reqId = `${serviceId}_${uri}`;
  queryFeatureList(reqId, cloudTmssUrl.value)
    .then((res) => {
      if (res?.status === 200 && res?.data?.status === 'success') {
        featureTreeData.value = handleNode(res?.data?.result, true);
      }
    })
    .catch(() => {
      cloudTestErrorFlag.value = true;
    });
};


const buildTreeNode = (id, label, name, isOpen, isParent = false) => {
  return {
    id,
    label: label || name || '',
    data: { type: 'folder', loading: false, isOpen },
    expanded: isOpen,
    isLeaf: false,
    isParent,
    children: [],
  };
};

const handleNode = (node: any, isOpen = false, treeNodes = []) => {
  if (!node) {
    return treeNodes;
  }
  const name = node.name ? node.name : 'Feature';
  const treeNode = buildTreeNode(node.uri, name, name, isOpen, true);
  treeNodes.push(treeNode);
  if (node?.value?.length) {
    node.value.forEach((child) => {
      handleNode(child, false, treeNode.children);
    });
  }
  return treeNodes;
};

const featureNodeClick = (node) => {
  selectedFeatureNode.value = node;
};

const refreshChildFeature = (node) => {
  if (node.data?.loading) return;
  node.children?.forEach((childNode) => {
    cloudTestTreeRef.value.treeFactory.removeNode(childNode);
  });
  node.isLeaf = false;
  node.isParent = true;
  node.data.loading = true;
  queryChildFeatureList(node.id, cloudTmssUrl.value)
    .then((res) => {
      if (res?.status === 200 && res?.data?.status === 'success') {
        const value = res?.data?.result?.value || [];
        if (value.length) {
          value.forEach((feature) => {
            const childNode = buildTreeNode(feature.uri, feature.name, feature.name, false, true);
            cloudTestTreeRef.value.treeFactory.insertBefore(node, childNode);
          });
        } else {
          node.isLeaf = true;
          node.isParent = false;
        }
        node.data.loading = false;
      }
    })
    .catch(() => {
      node.data.loading = false;
    });
};

const lazyLoadCloudTestTree = (node, callback) => {
  let childNodes: any = [];
  queryChildFeatureList(node.id, cloudTmssUrl.value)
    .then((res) => {
      if (res?.status === 200 && res?.data?.status === 'success') {
        const value = res?.data?.result?.value || [];
        if (value.length) {
          value.forEach((feature) => {
            const childNode = buildTreeNode(feature.uri, feature.name, feature.name, false, true);
            childNodes.push(childNode);
          });
        }
      }
      callback({ treeItems: childNodes, node });
    })
    .catch(() => {
      callback({ treeItems: childNodes, node });
    });
};

// ==================== 公共逻辑 ====================

const handleClose = () => {
  visible.value = false;
  saveCache(props.cloudTestConfig?.serviceId);
};

const resetState = () => {
  selectedSet.value.clear();
  archivedItems.value.clear();
  currentNode.value = {};
  hasSelectedItems.value = false;
  allCaseItems.value = [];
  caseDuplicateInfo.value.clear();
  if (isCloudTestPlatform()) {
    branchOptions.value = [];
    currentBranch.value = null;
    iterationOptions.value = [];
    currentIteration.value = null;
    featureTreeData.value = [];
    selectedFeatureNode.value = null;
    cloudTestErrorFlag.value = false;
  }
};

const handleConfirm = () => {
  if (isCloudTestPlatform()) {
    handleCloudTestConfirm();
  } else {
    handleCidaConfirm();
  }
};

const handleCidaConfirm = async () => {
  if (!currentNode.value.uri) {
    proxy.$notificationService.open({
      content: '请选择归档路径',
      duration: 3000,
      type: 'warning',
    });
    return;
  }
  if (currentNode.value.type === 'TestCase') {
    proxy.$notificationService.open({
      content: '不能在用例上归档',
      duration: 3000,
      type: 'warning',
    });
    return;
  }

  console.log("currentNode", currentNode)
  if (currentNode.value.type === 'TestCaseContainer') {
    proxy.$notificationService.open({
      content: '不能在Cases层归档',
      duration: 3000,
      type: 'warning',
    });
    return;
  }

  if (currentNode.value.type === 'BaselineVersion') {
    proxy.$notificationService.open({
      content: '不能在版本层级归档',
      duration: 3000,
      type: 'warning',
    });
    return;
  }
  if (!currentNode.value.type) {
    proxy.$notificationService.open({
      content: '不能在根目录归档',
      duration: 3000,
      type: 'warning',
    });
    return;
  }

  const selectedItems = allCaseItems.value.filter((item) => item.checked);
  if (!selectedItems.length) {
    proxy.$notificationService.open({
      content: "请选择要归档的用例",
      duration: 3000,
      type: 'warning',
    });
    return;
  }
  
  await checkDuplicateNumbers(selectedItems);
};

/**
 * 检查用例的编号是否已存在于TMSS
 */
const checkDuplicateNumbers = async (selectedItems: any[]) => {
  const numberSet = new Set<string>();
    selectedItems.forEach((item) => {
    if (item.number) {
      numberSet.add(item.number);
    }
  });

  if (!numberSet.size) {
    handleArchiveByInterface(selectedItems);
    return;
  }
  const uniqueNumbers = Array.from(numberSet);
  const scopePath = currentNode.value.versionPath;
  
  try {
    const caseInfos = uniqueNumbers.map((number) => ({ number }));
    const res = await queryCaseByNumbers(scopePath, caseInfos);
    
    if (res?.status === 200 && res?.data?.status === 'ok') {
      const result = res?.data?.result || [];
      const duplicateNumbers = result
        .filter((caseInfo: any) => caseInfo.uri)
        .map((caseInfo: any) => caseInfo.number);
      
      if (duplicateNumbers.length > 0) {
        const duplicateCases = selectedItems.filter((item) =>
          duplicateNumbers.includes(item.number)
        ).map((item) => ({
          name: item.name,
          number: item.number
        }));
        
        duplicateCaseList.value = duplicateCases;
        pendingArchiveItems.value = selectedItems;
        duplicateVisible.value = true;
      } else {
        handleArchiveByInterface(selectedItems);
      }
    } else {
      handleArchiveByInterface(selectedItems);
    }
  } catch (error) {
    console.error('检查用例编号失败:', error);
    handleArchiveByInterface(selectedItems);
  }
};

/**
 * 继续归档（存在重复编号时）
 */
const handleContinueArchive = () => {
  duplicateVisible.value = false;
  if (isCloudTestPlatform()) {
    archiveCloudTest(pendingArchiveItems.value);
  } else {
    handleArchiveByInterface(pendingArchiveItems.value);
  }
};

/**
 * 检查CloudTest用例的编号是否已存在
 */
const checkCloudTestDuplicateNumbers = async (selectedItems: any[]) => {
  const numberStageMap = new Map<string, string>();
  selectedItems.forEach((item) => {
    if (item.number) {
      numberStageMap.set(item.number, filterValues.value.stage?.value || '3');
    }
  });

  if (!numberStageMap.size) {
    archiveCloudTest(selectedItems);
    return;
  }

  const scopePath = currentBranch.value?.uri;
  if (!scopePath) {
    archiveCloudTest(selectedItems);
    return;
  }

  try {
    const caseInfos = Array.from(numberStageMap.entries()).map(([number, stage]) => ({
      number,
      stage
    }));
    
    const res = await queryCloudTestCaseByNumbers(scopePath, caseInfos);
    
    if (res?.status === 200 && res?.data?.status === 'ok') {
      const result = res?.data?.result?.value || [];
      const duplicateNumbers = result.map((caseInfo: any) => caseInfo.number);
      
      if (duplicateNumbers.length > 0) {
        const duplicateCases = selectedItems.filter((item) =>
          duplicateNumbers.includes(item.number)
        ).map((item) => ({
          name: item.name,
          number: item.number
        }));
        
        duplicateCaseList.value = duplicateCases;
        pendingArchiveItems.value = selectedItems;
        duplicateVisible.value = true;
      } else {
        archiveCloudTest(selectedItems);
      }
    } else {
      archiveCloudTest(selectedItems);
    }
  } catch (error) {
    console.error('检查CloudTest用例编号失败:', error);
    archiveCloudTest(selectedItems);
  }
};

const handleCloudTestConfirm = async () => {
  if (!selectedFeatureNode.value) {
    proxy.$notificationService.open({
      content: '请选择Feature目录',
      duration: 3000,
      type: 'warning',
    });
    return;
  }
  if (selectedFeatureNode.value.id === featureTreeData.value[0]?.id && !selectedFeatureNode.value.children?.length) {
    proxy.$notificationService.open({
      content: '禁止在Feature根目录直接归档用例',
      duration: 3000,
      type: 'warning',
    });
    return;
  }

  const selectedItems = allCaseItems.value.filter((item) => item.checked);
  if (!selectedItems.length) {
    proxy.$notificationService.open({
      content: '请选择要归档的用例',
      duration: 3000,
      type: 'warning',
    });
    return;
  }
  
  await checkCloudTestDuplicateNumbers(selectedItems);
};

/**
 * 构建测试用例参数
 */
const buildTestCaseParam = (caseInfo: any) => {
  return {
    featureUri: selectedFeatureNode.value.id,
    stage: filterValues.value?.stage?.value || '',
    testType: filterValues.value?.type?.value || '0',
    activity: filterValues.value?.testPlatform?.value || '',
    author: props.userInfo?.id,
    name: caseInfo.name,
    number: caseInfo.number,
    autotype: caseInfo.autotype || '0',
    preparation: caseInfo.pre,
    testStep: caseInfo.test_step,
    expectOutput: caseInfo.expect_output,
    rank: rankMapping[caseInfo.priority] || '2',
    customField23: '3',
  };
};

/**
 * 处理批量归档成功结果
 */
const processBatchSuccess = (batchCaseItems: any[], caseList: any[], successCaseItems: any[], archivedTcList: any[]) => {
  batchCaseItems.forEach((batchCaseInfo) => {
    const caseInfo = caseList.find((c) => c.number === batchCaseInfo.number);
    if (caseInfo) {
      const url = getCloudTestUrl(caseInfo);
      successCaseItems.push({
        number: batchCaseInfo.number,
        uuid: batchCaseInfo.uuid,
        uri: caseInfo.uri,
        url: url,
        tmssArchivedStatus: ARCHIVE_STATUS.ARCHIVED,
      });

      archivedTcList.push({
        uri: caseInfo.uri,
        session_id: props.session.id,
        user_id: props.userInfo?.id,
        number: caseInfo.number,
        tc_url: url,
        tool_type: 'CloudTest',
        project_id: props.projectId,
        create_time: caseInfo.creationDate
      });
    }
  });
  
  batchCaseItems.forEach(bItem => archivedItems.value.add(bItem.uuid || bItem.name));
};

/**
 * 处理批量归档失败结果
 */
const processBatchFailure = (batchCaseItems: any[], reason: string, failedItems: any[]) => {
  batchCaseItems.forEach(item => {
    failedItems.push({
      name: item.name,
      reason: reason || '归档失败'
    });
  });
};

/**
 * 归档单个批次
 */
const archiveSingleBatch = async (versionUri: string, batchCaseItems: any[], successCaseItems: any[], archivedTcList: any[], failedItems: any[]) => {
  const params = batchCaseItems.map(buildTestCaseParam);
  
  try {
    const res = await createCloudTestCase(versionUri, params);
    
    if (res?.status === 200 && res?.data?.status === 'ok') {
      const caseList = res?.data?.result?.value?.length ? res.data.result.value : [];
      processBatchSuccess(batchCaseItems, caseList, successCaseItems, archivedTcList);
      return { success: true, count: batchCaseItems.length };
    } else {
      const reason = res?.data?.result?.reason || res?.data?.message || '归档失败';
      processBatchFailure(batchCaseItems, reason, failedItems);
      return { success: false, count: batchCaseItems.length };
    }
  } catch (err) {
    processBatchFailure(batchCaseItems, err.message, failedItems);
    return { success: false, count: batchCaseItems.length };
  }
};

/**
 * 显示归档结果
 */
const showArchiveResult = (successNum: number, failedNum: number, successCaseItems: any[], failedItems: any[]) => {
  if (failedNum === 0) {
    proxy.$notificationService.open({
      content: `用例归档：成功${successNum}条`,
      duration: 3000,
      type: 'success',
    });
    emit('confirm', { successCaseItems });
  } else {
    failedTableData.value = failedItems;
    failedVisible.value = true;
    proxy.$notificationService.open({
      content: `用例归档：成功${successNum}条，失败${failedNum}条`,
      duration: 5000,
      type: 'warning',
    });
  }
};

/**
 * 归档CloudTest用例
 */
const archiveCloudTest = async (items: Array<any>) => {
  confirmLoading.value = true;
  
  const versionUri = currentIteration.value?.uri || currentBranch.value.uri;
  const batchSize = 200;
  const caseItems = items;
  const totalBatches = Math.ceil(caseItems.length / batchSize);
  
  let successNum = 0;
  let failedNum = 0;
  const failedItems = [];
  const successCaseItems = [];
  const archivedTcList = [];
  
  for (let i = 0; i < caseItems.length; i += batchSize) {
    const batchIndex = Math.floor(i / batchSize) + 1;
    const batchCaseItems = caseItems.slice(i, i + batchSize);
    
    const result = await archiveSingleBatch(versionUri, batchCaseItems, successCaseItems, archivedTcList, failedItems);
    
    if (result.success) {
      successNum += result.count;
    } else {
      failedNum += result.count;
    }
    
    if (batchIndex < totalBatches) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  createCloudTestRelations(successCaseItems);
  createCloudTestCaseRequirementRelations(successCaseItems);
  
  if (archivedTcList.length > 0) {
    sessionRecode({
      type: 'testdesign-testcase',
      data: archivedTcList
    });
  }

  confirmLoading.value = false;
  showArchiveResult(successNum, failedNum, successCaseItems, failedItems);
};

const getCaseItems = (items: Array<any>) => {
  if (!items?.length) {
    return [];
  }
  const caseItems = [];
  items.forEach(item => {
    if (item.test_case_list?.length) {
      item.test_case_list.forEach(caseItem => {
        caseItems.push(caseItem);
      });
    }
  });
  return caseItems;
};

const getCloudTestUrl = (caseInfo: any) => {
  if (!caseInfo) {
    return '';
  }
  const domain = `${import.meta.env.VITE_CLOUDTEST_URL}`;
  const { groupId, serviceId } = props.cloudTestConfig;
  // 分支uri和迭代uri需要获取选中的值
  const branchUri = currentBranch.value.uri;
  const iterationUri = getVersionUri();
  return `${domain}/cloudtest/project/${groupId}/testCaseDetail?caseUri=${
    caseInfo.IteratorCaseUri || caseInfo.uri
  }&serviceId=${serviceId}&cloudVersionUri=${branchUri ?? ''}&cloudIteratorUri=${iterationUri ?? ''}`;
};

/**
 * 创建用例和sessionId sessionUrl关系
 */
 const createCloudTestRelations = (caseList) => {
  if (!caseList?.length) {
    return;
  }
  const url = window.parent.location.href;
  const uris = Array.from(new Set(caseList.map((caseInfo) => caseInfo.uri).filter(Boolean)));
  const sId = props.session?.id ? props.session?.id : '';
  const param = {
    version_uri: getVersionUri(),
    testcase_uris: uris,
    test_mind_url: url,
    test_mind_id: String(sId),
  };
  createTcRelationByCloudTest(param).then();
};

/**
 * 创建CloudTest用例和需求关联关系
 */
const createCloudTestCaseRequirementRelations = async (caseList) => {
  try {
    // 1. 检查是否有需求信息
    if (!props.data?.reqType) {
      console.log('没有需求类型，跳过创建关联关系');
      return;
    }

    // 2. 获取版本URI
    const versionUri = currentBranch.value?.uri;
    if (!versionUri) {
      console.log('没有版本URI，跳过创建关联关系');
      return;
    }

    // 3. 提取用例uri
    const caseUris = caseList.map(caseInfo => caseInfo.uri).filter(Boolean);
    if (!caseUris?.length) {
      console.log('没有有效的用例uri，跳过创建关联关系');
      return;
    }

    // 4. 获取需求编号
    const nums = getCloudTestReqNums();
    if (!nums?.length) {
      console.log('没有需求编号，跳过创建关联关系');
      return;
    }

    // 5. 构造请求参数
    const relations = [];
    caseUris.forEach((testCaseUri) => {
      nums.forEach((drNumber) => {
        relations.push({
          testCaseUri,
          drNumber,
          relateType: 'requirement',
        });
      });
    });

    const param = { relations };

    // 6. 创建用例和需求关联关系
    const relationRes = await createCloudTestCaseReqRelation(versionUri, param);
    if (relationRes?.status === 200) {
      console.log('CloudTest用例和需求关联关系创建成功');
    } else {
      console.error('CloudTest用例和需求关联关系创建失败:', relationRes?.data?.message);
    }
  } catch (error) {
    console.error('创建CloudTest用例和需求关联关系异常:', error);
  }
};

const getCloudTestReqNums = () => {
  const isIone = props.data.reqType === 'RequirementIone';
  if (props.data?.treeType === 'taskTree' && props.data?.req_origin_info?.length) {
    return props.data.req_origin_info.map((req) => {
      if (isIone) {
        return req.number;
      } else {
        return req.id;
      }
    });
  } else {
    const drNumber = isIone ? props.data.requirement_number : props.data.requirement_id;
    return [drNumber].filter(Boolean);
  }
};

const getVersionUri = () => {
    return currentIteration.value?.uri || currentBranch.value?.uri;
}

/**
 * 处理单个用例归档成功
 */
const handleArchiveSuccess = (item: any, caseInfo: any, successCaseItems: any[], archivedTcList: any[]) => {
  archivedItems.value.add(item.uuid || item.name);
  selectedSet.value.delete(item.name);
  
  const url = getCidaUrl(caseInfo);
  successCaseItems.push({
    number: item.number,
    uuid: item.uuid,
    uri: caseInfo.realURI,
    url: url,
    tmssArchivedStatus: ARCHIVE_STATUS.ARCHIVED,
  });
  
  hasSelectedItems.value = selectedSet.value.size > 0;
  
  archivedTcList.push({
    uri: caseInfo.realURI,
    number: item.number,
    session_id: props.session.id,
    user_id: props.userInfo?.id,
    tc_url: url,
    tool_type: 'CIDA',
    project_id: props.projectId,
    create_time: caseInfo.creationDate
  });
};

/**
 * 处理单个用例归档失败
 */
const handleArchiveFailure = (itemName: string, reason: string, failedItems: any[]) => {
  failedItems.push({
    name: itemName,
    reason: reason || '归档失败'
  });
};

/**
 * 归档单个用例
 */
const archiveSingleCase = async (item: any, successCaseItems: any[], archivedTcList: any[], failedItems: any[]) => {
  const parentDirectories = getParentDirectories(currentNode.value.id);
  
  const tcParams = {
    context_xml: JSON.stringify(transformToCidaRequest(item, null, props.session)),
    version_path: currentNode.value.versionPath,
    parent_directories: parentDirectories,
    ignore_revision: true,
    only_name_same_update: false,
  };
  
  try {
    const res = await cidaCaseArchive(props.projectId, tcParams);
    const uri = res?.data?.result?.value;
    
    if (res.status === 200 && res?.data?.status === 'ok' && uri) {
      const caseInfo = {
        realURI: uri.split('/').filter(e => e).pop(),
        uri,
        spaceUri: currentNode.value.spaceUri,
        creationDate: formatDateTime(),
      };
      handleArchiveSuccess(item, caseInfo, successCaseItems, archivedTcList);
      return { success: true };
    } else {
      handleArchiveFailure(item.name, res.data?.result?.reason, failedItems);
      return { success: false };
    }
  } catch (err) {
    handleArchiveFailure(item.name, err.message, failedItems);
    return { success: false };
  }
};

const formatDateTime = (date = new Date()) => {
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(
    date.getSeconds()
  )}`;
};

/**
 * 创建CIDA平台的用例和需求关联关系
 */
const createCidaCaseRequirementRelations = async (successCaseItems: any[]) => {
  if (!successCaseItems?.length) {
    return;
  }
  if (props.data?.reqType === 'alm') {
    await createCidaCaseRequirementRelation(successCaseItems);
  } else if (props.data?.reqType === 'cloudalm') {
    await createCloudAlmCaseRequirementRelation(successCaseItems);
  }
};

/**
 * 显示CIDA归档结果
 */
const showCidaArchiveResult = (successNum: number, failedNum: number, successCaseItems: any[], failedItems: any[]) => {
  if (failedNum > 0) {
    failedTableData.value = failedItems;
    failedVisible.value = true;
    proxy.$notificationService.open({
      content: `用例归档：成功${successNum}条，失败${failedNum}条`,
      duration: 3000,
      type: 'warning',
    });
  } else {
    proxy.$notificationService.open({
      content: `用例归档：成功${successNum}条，失败${failedNum}条`,
      duration: 3000,
      type: 'success',
    });
  }
};

/**
 * 归档CIDA用例
 */
const handleArchiveByInterface = async (selectedItems: any[]) => {
  let successNum = 0;
  let failedNum = 0;
  const failedItems = [];
  const successCaseItems = [];
  const archivedTcList = [];
  for (const item of selectedItems) {
    const result = await archiveSingleCase(item, successCaseItems, archivedTcList, failedItems);
    
    if (result.success) {
      successNum++;
    } else {
      failedNum++;
    }
  }
  showCidaArchiveResult(successNum, failedNum, successCaseItems, failedItems);
  emit('confirm', { successCaseItems });
  createCidaRelations(successCaseItems);
  await createCidaCaseRequirementRelations(successCaseItems);
  if (archivedTcList.length > 0) {
    sessionRecode({
      type: 'testdesign-testcase',
      data: archivedTcList
    });
  }
};

const getCidaUrl = (caseInfo) => {
  if (!caseInfo) {
    return '';
  }
  return `spaceUri=${caseInfo.spaceUri}&resourceUri=${caseInfo.uri}`;
};

/**
 * 创建用例和sessionId sessionUrl关系
 */
 const createCidaRelations = async (caseList) => {
  if (!caseList?.length) {
    return;
  }
  
  const url = window.parent.location.href;
  const uris = Array.from(new Set(caseList.map((caseInfo) => caseInfo.uri).filter(Boolean)));
  const sId = props.session?.id ? props.session?.id : '';
  const param = {
    version_uri: currentNode.value.versionPath.split('/').filter(Boolean)[1],
    res_uris: uris,
    test_mind_url: url,
    test_mind_id: String(sId),
  };
  createTcRelationByCida(param).then();
};

/**
 * 创建用例和需求关联关系（仅针对CIDA平台的ALM需求系统）
 */
const createCidaCaseRequirementRelation = async (caseList) => {
  try {
    // 1. 检查是否有需求编号
    const nums = getAlmReqNums();
    if (!nums?.length) {
      console.log('没有需求ID或需求编号，跳过创建关联关系');
      return;
    }
    
    // 2. 检查用例是否有versionPath
    if (!currentNode.value?.versionPath) {
      console.log('用例没有版本路径信息，跳过创建关联关系');
      return;
    }
    
    // 3. 获取用例版本路径（格式：/003rfk9iun0/01srokrq0nc/）
    const versionPathParts = currentNode.value.versionPath.split('/').filter(Boolean);
    if (versionPathParts.length < 2) {
      console.log('版本路径格式不正确，跳过创建关联关系');
      return;
    }
    const scope = `/${versionPathParts[0]}/${versionPathParts[1]}/`;
    
    // 4. 查询需求的rmUri
    const rmUriRes = await queryRmUriByNumber(scope, nums);
    if (rmUriRes?.status === 200 && rmUriRes?.data?.status === 'ok') {
      const rmUris = rmUriRes?.data?.result?.value?.rmUris || [];
      const notExistsNum = rmUriRes?.data?.result?.value?.notExistsNum || [];
      
      // 检查是否有查询失败的编号
      if (notExistsNum?.length) {
        console.warn('以下需求编号不存在或无法查询到rmUri:', notExistsNum);
      }
      
      if (!rmUris?.length) {
        console.log('没有查询到需求的rmUri，跳过创建关联关系');
        return;
      }
      
      // 6. 获取用例的uri列表
      const caseUris = caseList.map(caseInfo => caseInfo.uri).filter(Boolean);
      if (!caseUris?.length) {
        console.log('没有有效的用例uri，跳过创建关联关系');
        return;
      }
      
      // 7. 创建用例和需求关联关系
      const relationParam = {
        associatedResourcePaths: caseUris,
        paths: rmUris,
        relation_add_type: 'ONLY_LOGIC_TC'
      };
      
      const relationRes = await createCaseReqRelation(relationParam);
      if (relationRes?.status === 200 && relationRes?.data?.status === 'ok') {
        console.log('用例和需求关联关系创建成功');
      } else {
        console.error('用例和需求关联关系创建失败:', relationRes?.data?.result?.reason || relationRes?.data?.message);
      }
    } else {
      console.error('查询需求rmUri失败:', rmUriRes?.data?.result?.reason || rmUriRes?.data?.message);
    }
  } catch (error) {
    console.error('创建用例和需求关联关系异常:', error);
  }
};

const getAlmReqNums = () => {
  if (props.data?.treeType === 'taskTree' && props.data?.req_origin_info?.length) {
    return props.data.req_origin_info.map((req) => req.number);
  } else if (props.data?.requirement_number) {
    return [props.data.requirement_number];
  } else {
    return [];
  }
};

/**
 * 创建CloudALM需求和用例关联关系（仅针对CIDA平台的CloudALM需求系统）
 */
const createCloudAlmCaseRequirementRelation = async (caseList) => {
  try {
    // 1. 检查是否有需求信息
    const reqs = getCloudAlmReqs();
    if (!reqs?.length) {
      console.log('没有需求ID或需求编号，跳过创建关联关系');
      return;
    }

    // 2. 检查用例是否有versionPath
    if (!currentNode.value?.versionPath) {
      console.log('用例没有版本路径信息，跳过创建关联关系');
      return;
    }

    // 3. 获取用例版本路径（格式：/003rfk9iun0/01srokrq0nc/）
    const versionPathParts = currentNode.value.versionPath.split('/').filter(Boolean);
    if (versionPathParts.length < 2) {
      console.log('版本路径格式不正确，跳过创建关联关系');
      return;
    }
    const versionUri = versionPathParts[1];

    // 4. 获取用例的uri列表
    const caseUris = caseList.map((caseInfo) => caseInfo.uri).filter(Boolean);
    if (!caseUris?.length) {
      console.log('没有有效的用例uri，跳过创建关联关系');
      return;
    }

    // 5. 构造请求参数
    const param = reqs.map((req) => ({
      upUri: req.id,
      upType: 'RMResource',
      upNumber: req.number,
      sourceSystem: 'cloudalm',
      domain: '',
      versionAndMultiResUris: [
        {
          relation_add_type: 'ONLY_LOGIC_TC',
          versionUri: versionUri,
          resType: 'TestCase',
          resUris: caseUris,
        },
      ],
    }));

    // 6. 创建用例和需求关联关系
    const relationRes = await createCloudAlmCaseReqRelation(param);
    if (relationRes?.status === 200 && relationRes?.data?.status === 'ok') {
      console.log('CloudALM用例和需求关联关系创建成功');
    } else {
      console.error('CloudALM用例和需求关联关系创建失败:', relationRes?.data?.result?.reason || relationRes?.data?.message);
    }
  } catch (error) {
    console.error('创建CloudALM用例和需求关联关系异常:', error);
  }
};

const getCloudAlmReqs = () => {
  if (props.data?.treeType === 'taskTree' && props.data?.req_origin_info?.length) {
    return props.data.req_origin_info;
  } else if (props.data?.requirement_number) {
    return [
      {
        id: props.data.requirement_id,
        number: props.data.requirement_number,
      },
    ];
  } else {
    return [];
  }
};

const getAllCase = () => {
  if (!props.selectData?.length) {
    allCaseItems.value = [];
    caseDuplicateInfo.value.clear();
    return;
  }
  const list: any[] = [];
  props.selectData.forEach((tp: any) => {
    if (tp?.test_case_list?.length) {
      tp.test_case_list.forEach((c) => {
        list.push(c);
      });
    }
  });
  
  caseDuplicateInfo.value.clear();
  
  const numberIndexMap = new Map<string, number>();
  const nameIndexMap = new Map<string, number>();
  
  list.forEach((item, index) => {
    const itemNumber = item.number || '';
    const itemName = item.name || '';
    
    if (itemNumber && numberIndexMap.has(itemNumber)) {
      const firstIndex = numberIndexMap.get(itemNumber)!;
      caseDuplicateInfo.value.set(index, {
        disabled: true,
        reason: `与序号${firstIndex + 1}的用例编号相同`
      });
    } else if (isCidaPlatform() && itemName && nameIndexMap.has(itemName)) {
      const firstIndex = nameIndexMap.get(itemName)!;
      caseDuplicateInfo.value.set(index, {
        disabled: true,
        reason: `与序号${firstIndex + 1}的用例名称相同`
      });
    } else {
      if (itemNumber) {
        numberIndexMap.set(itemNumber, index);
      }
      if (isCidaPlatform() && itemName) {
        nameIndexMap.set(itemName, index);
      }
      caseDuplicateInfo.value.set(index, {
        disabled: false,
        reason: ''
      });
    }
  });
  
  allCaseItems.value = list;
};

const isCidaPlatform = () => {
  return props.platform === 'cida';
};

const isCloudTestPlatform = () => {
  return props.platform === 'cloudtest';
};

const scrollNodeUri = ref('');

watch(
  () => props.modelValue,
  val => {
    visible.value = val;
  },
  { immediate: true }
);

watch(visible, val => {
  emit('update:modelValue', val);
  if (val) {
    getAllCase();
    if (isCloudTestPlatform()) {
      initCloudTestTree();
    } else {
      getTreeData();
    }
  } else {
    resetState();
  }
});

const isChecked = computed(() => {
  return allCaseItems.value.some((item) => item.checked);
});
</script>
<style lang="scss" scoped>
.archive-dialog-content {
  display: flex;
  gap: 16px;
  min-height: 600px;
  max-height: 500px;
}

.archive-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.case-list-section {
  max-width: 320px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}

.section-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.case-count {
  font-size: 12px;
  color: #999;
}

.select-all {
  margin-left: 20px;
}

.select-all > .select-all-title {
  margin-left: 5px;
}

.case-list-wrapper {
  flex: 1;
  overflow-y: auto;
  background: #fafafa;
  border-radius: 4px;
  padding: 8px;
}

.case-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 4px;
  background: #fff;
  border-radius: 4px;
  font-size: 13px;
  color: #333;
  border: 1px solid #f0f0f0;
  transition: border-color 0.2s;
  word-break: break-word;
  line-height: 1.5;

  input[type='checkbox'] {
    width: 14px;
    height: 14px;
    accent-color: #5e7ce0;
    cursor: pointer;
    border: 1px solid #dbdbdb;
  }

  &:last-child {
    margin-bottom: 0;
  }
  
  &.is-disabled {
    opacity: 0.6;
    background: #f5f5f5;
    cursor: not-allowed;
    
    .icon-ban {
      width: 14px;
      height: 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: #999; font-size: 14px; 
      margin: 0 3px 0 4px;
    }
  }
}

.case-index {
  flex-shrink: 0;
  width: 24px;
  font-size: 12px;
  text-align: center;
}

.case-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archived-tag {
  flex-shrink: 0;
  padding: 2px 6px;
  font-size: 11px;
  color: #52c41a;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 3px;
}

.empty-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 13px;
}

.archive-divider {
  width: 1px;
  background: #e8e8e8;
  margin: 0 4px;
}

.tree-section {
  .section-header {
    padding-left: 12px;
  }
}

.tmss-tree {
  flex: 1;
  max-height: calc(100% - 40px);
  overflow-y: auto;
}

.title-merge {
  display: flex;
  align-items: center;
  margin: 5px 20px 5px 0;
  height: 28px;

  .label-text {
    display: inline-block;
    width: 70px;
    flex-shrink: 0;
  }

  .default-select {
    flex: 1;
    min-width: 0;
  }
}

.cloud-test-tree {
  flex: 1;
  max-height: calc(100% - 140px);
  overflow-y: auto;
  margin-top: 8px;
}

.custom-tree-node {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

:deep(.dv-tree__node .dv-tree__node-content--value-wrapper) {
  overflow: unset;
}

:deep(.dv-tree__node .dv-tree__drag-bound-line) {
  overflow: unset;
}

.op-icons {
  display: inline-block;
  margin-left: 8px;
  cursor: pointer;
  color: #575d6c;
  font-size: 12px;

  &:hover {
    color: #5e7ce0;
  }
}

.icon-folder {
  color: #fa9841;
}

.icon-test-manager {
  color: #5ebf75;
}

.link {
  color: #5e7ce0;
  cursor: pointer;

  &:hover {
    color: #405dff;
  }
}

.failed-table {
  max-height: 400px;
}
</style>
