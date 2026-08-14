import axios from 'axios';
import { ref, computed } from 'vue';
import { UserStore } from "@/stores/user";
import type { CidaBatchImportParams, CloudTestImportParams } from './type';


// api.ts 顶部添加
let _tmssBaseUrl = '';
export const setTmssBaseUrl = (url: string) => { _tmssBaseUrl = url; };
export const getTmssBaseUrl = () => _tmssBaseUrl;

const apiPrefix = import.meta.env.VITE_API_PREFIX || '/aidigital-test';

const _loadingCounter = ref(0);
export const apiLoading = computed(() => _loadingCounter.value > 0);

const showLoading = () => { _loadingCounter.value++; };
const hideLoading = () => { _loadingCounter.value = Math.max(0, _loadingCounter.value - 1); };

/**
 * 接口客户端请求实例
 * 创建 axios 实例，配置基础 URL 和凭证选项
 */
const clientAxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_CLIENT_API_BASE_URL,
  withCredentials: false,
});

/**
 * 接口agent平台请求实例
 * 创建 axios 实例，配置基础 URL 和凭证选项
 */
const agentAxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_TEST_AGENT_API_BASE_URL,
  withCredentials: false,
});

agentAxiosInstance.interceptors.request.use(
  (config) => { showLoading(); return config; },
  (error) => { hideLoading(); return Promise.reject(error); }
);
agentAxiosInstance.interceptors.response.use(
  (response) => { hideLoading(); return response; },
  (error) => { hideLoading(); return Promise.reject(error); }
);

export const getCookie = (key: string) => {
  const arr = document.cookie.match(new RegExp(`(^|)${key}=([^;]*)(;|$)`));
  if (arr !== null) {
    return decodeURIComponent(arr[2]) || '';
  }
  return '';
};

export const getCftkValue = (env): string => {
  return getCookie(env === 'gamma' ? 'prod_gamma_cftk' : 'prod_cftk');
}

const agentHeader = () => {
  let header = {
    "cftk": getCftkValue(import.meta.env.VITE_ENV_NAME),
    "x-requested-with": "XMLHttpRequest",
    "UserName": UserStore().userInfo.id,
    "requestId": new Date().getMilliseconds()
  }
  return header
}

/**
 * 记录用例回填结果
 * 将测试用例的执行结果同步到后端系统
 * @param params.tid - 任务ID
 * @param params.id - 用例ID
 * @param params.result - 测试结果
 * @returns Promise - 返回请求结果的 Promise 对象
 */
export const recordTestCaseResult = (params: { tid: string; id: string; result: string }) => {
  return clientAxiosInstance.post(`/digital-test/agent/v1/result/update`, params);
};

export const openFile = (params: { extension_id: string; extension_version: string;}) => {
  return clientAxiosInstance.post(`/digital-test/agent/v1/directory/open`, params);
};

/**
 * 服务端接口请求实例
 * 创建 axios 实例，配置基础 URL 和凭证选项
 */
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_TASS_API_BASE_URL,
  withCredentials: true,
});

/**
 * 测试点归档
 * 批量将测试结果回填到测试管理系统
 * @param params.root - 归档结构
 */
export const mindmapCreateOrUpdateByAi = (data, userInfo) => {
  return agentAxiosInstance.post(`${apiPrefix}/ServiceHtsm/GeneralHTSM/strategy/createOrUpdateByAi`, data,
      {headers: agentHeader()}
  );
};

// 归档后上传
export const mindmapUpload = (data, info) => {
  const formData = new FormData();
  Object.keys(data).forEach(key => {
    formData.append(key, data[key]);
  });
  return agentAxiosInstance.post('/aidigital-test/ServiceHtsm/GeneralHTSM/v1/third-party/filelib/upload', formData,
      {headers: {...agentHeader(), 'Content-Type': 'multipart/form-data'}}
  );
};

/**
 * 基于左侧需求树做设计需要先创建测试设计任务
 *
 * @param cidaProjectId
 * @param param
 */
export function createTask(cidaProjectId, param) {
  return agentAxiosInstance.post(`${apiPrefix}/ServiceCBTask/v1/items/task/createTask?projectId=${cidaProjectId}`, param, {headers: agentHeader()});
}



/**
 * 获取子节点信息
 *
 * @param id
 */
export function getChildrenNode(uri, param) {
  return agentAxiosInstance.get(`${apiPrefix}/${_tmssBaseUrl}/GT3KServer/v1/resource/children/${uri}`,{headers: {...agentHeader(), "clienttype": "cida"}, params: param});
}

/**
 * 查询树节点路径
 *
 * @param param
 */
export function getNamePaths(param) {
  return agentAxiosInstance.post(`${apiPrefix}/${_tmssBaseUrl}/GT3KServer/v0/resource/namePaths`, param,
      {headers: {...agentHeader(), "clienttype": "cida"}});
}

/**
 * 归档用例
 *
 * @param parentUri
 * @param param
 */
export function useCaseArchive(projectId, parentUri, param) {
  return agentAxiosInstance.post(`${apiPrefix}/${_tmssBaseUrl}/GT3KServer/v1/resource/detail/${parentUri}`, param,
      {headers: {...agentHeader(), "clienttype": "cida", "projectid": projectId}});
}

/**
 * 归档CIDA用例
 *
 * @param projectId 项目id
 * @param param 用例参数
 */
export function cidaCaseArchive(projectId, param) {
  return agentAxiosInstance.post(`${apiPrefix}/${_tmssBaseUrl}/GT3KServer/v3/testcase/sync`, param,
      {headers: {...agentHeader(), clienttype: 'cida', projectid: projectId}});
}

/**
 * 获取项目信息
 *
 * @param cidaProjectId
 */
export function getProjectInfo(cidaProjectId) {
  return agentAxiosInstance.get(`${apiPrefix}/cidaPlatform/v1/param?projectId=${cidaProjectId}&appId=&projectFlowId=`, {headers: agentHeader()});
}

export function getCloudTestIterationByServiceId(param: { tmssUrl: string; serviceId: string }) {
  return agentAxiosInstance.get(`${apiPrefix}/ServiceHtsm/GeneralHTSM/v1/getCloudTestIterationByServiceId`, { params: param, headers: agentHeader() });
}

export function getCloudTestIteration(branchUri: string) {
  return agentAxiosInstance.get(`${apiPrefix}/cd-tmss/v2/version/iterators`, {
    params: { versionUri: branchUri },
    headers: { ...agentHeader(), clienttype: 'HTSM' }
  });
}

export function getCloudTestBranchInfo(branchUri: string) {
  return agentAxiosInstance.get(`${apiPrefix}/cd-tmss/v5/version/${branchUri}`, {
    headers: { ...agentHeader(), clienttype: 'HTSM' }
  });
}

export function queryFeatureList(reqId: string, tmssUrl: string) {
  return agentAxiosInstance.post(`${apiPrefix}/ServiceHtsm/GeneralHTSM/v1/query/parentFeature/tree?reqId=${reqId}&tmssUrl=${tmssUrl}`, {}, { headers: agentHeader() });
}

export function queryChildFeatureList(uri: string, tmssUrl: string) {
  return agentAxiosInstance.post(`${apiPrefix}/ServiceHtsm/GeneralHTSM/v1/query/childrenFeature/tree?uri=${uri}&tmssUrl=${tmssUrl}`, {}, { headers: agentHeader() });
}

/**
  * 通过cloudTest的项目id获取配置
  * @param groupId 项目ID
  * @returns 配置项
  */
export function queryCloudTestConfigByProjectId(groupId: string) {
  return agentAxiosInstance.get(`${apiPrefix}/cd-atcase-no-prefix/v3/group/config/batch-query/${groupId}`, { headers: agentHeader() });
}

/**
  * 根据服务ID获取cloudTest服务配置的活动
  * @param serviceId 服务ID
  * @returns 活动
  */
export function getCloudTestActivityService(serviceId: string) {
  return agentAxiosInstance.get(`${apiPrefix}/cd-atcase/v1/testservice/${serviceId}`, {
    headers: agentHeader(),
  });
}

export function createCloudTestCase(versionUri: string, param) {
  return agentAxiosInstance.post(
    `${apiPrefix}/cd-tmss/v2/testcases?parentUri=${versionUri}&return_iterator_case=true`,
    param,
    {
      headers: { ...agentHeader(), clienttype: 'HTSM' },
    }
  );
}

export function getCloudTestServiceById(serviceId: string) {
  return agentAxiosInstance.get(`${apiPrefix}/cd-atcase-no-prefix/v3/test-services/${serviceId}`, {
    headers: agentHeader(),
  });
}

/**
 * session打点
 *
 */
export function sessionRecode(param) {
  return agentAxiosInstance.post(`${apiPrefix}/ServiceHtsm/GeneralHTSM/archive/forai/testdata`, param, {headers: agentHeader()});
}

export function createTcRelationByCloudTest(params: any) {
  return agentAxiosInstance.post(`${apiPrefix}/cd-tmss/v2/testcase-testmind/relations`, params, {
    headers: { ...agentHeader(), clienttype: 'HTSM' },
  });
}

export function createTcRelationByCida(params: any) {
  return agentAxiosInstance.post(`${apiPrefix}/${_tmssBaseUrl}/GT3KServer/v3/testcase-testmind/relations`, params, {
    headers: { ...agentHeader(), clienttype: 'HTSM' },
  });
}

/**
 * CloudTest平台：根据用例编号和阶段查询用例是否已存在
 * @param scopePath - 分支uri
 * @param caseInfos - 用例编号和阶段信息数组
 * @returns Promise - 返回查询结果，result中包含已存在的用例信息
 */
export function queryCloudTestCaseByNumbers(scopePath: string, caseInfos: Array<{ number: string; stage: string }>) {
  return agentAxiosInstance.post(
    `${apiPrefix}/cd-tmss/v3/search/testcase/numbers`,
    {
      scope_path: scopePath,
      case_infos: caseInfos
    },
    { headers: { ...agentHeader(), clienttype: 'HTSM' } }
  );
}

/**
 * 根据用例编号查询用例是否已存在于指定scope_path
 * @param scopePath - 作用域路径
 * @param caseInfos - 用例编号信息数组
 * @returns Promise - 返回查询结果，result中包含number和对应的uri
 */
export function queryCaseByNumbers(scopePath: string, caseInfos: Array<{ number: string }>) {
  return agentAxiosInstance.post(
    `${apiPrefix}/${_tmssBaseUrl}/GT3KServer/v3/testcase/uri/numbers`,
    {
      scope_path: scopePath,
      case_infos: caseInfos
    },
    { headers: { ...agentHeader(), clienttype: 'cida' } }
  );
}

/**
 * 获取驱动器列表
 * 获取本地计算机的所有驱动器信息
 */
export function getDrives() {
  const url = `/digital-test/agent/v1/directory/drives`; // http://localhost:8080/api/drives
  return clientAxiosInstance.get(url);
}

/**
 * 获取目录列表
 * 获取指定路径下的文件和目录列表
 * @param path - 目录路径
 */
export function listDirectory(path: string) {
  const url = `/digital-test/agent/v1/directory/list`; // http://localhost:8080/api/list
  return clientAxiosInstance.get(url, {
    params: { path }
  });
}

/**
 * 通过agent打开idea、pycharm等ide
 * @param param 
 * @returns 
 */
export function openIde(param) {
  return clientAxiosInstance.post(`/digital-test/agent/v1/directory/open-ide`, param, {headers: agentHeader()});
}

/**
 * 根据基线用例编号查询B版本用例
 * 判断指定用例编号是否存在于某个B版本路径下
 * @param numbers - 用例编号数组
 * @param scopePaths - B版本路径数组
 * @returns Promise - 返回查询结果，res_uris非空表示存在
 */
export function checkCaseInBVersion(numbers: string[], scopePaths: string[]) {
  return agentAxiosInstance.post(
    `${apiPrefix}/${_tmssBaseUrl}/hutaf_tmss_search/v4/search/testcase/numbers`,
    {
      numbers,
      scope_paths: scopePaths,
      res_type: 'TestCase',
      include_b_version: false
    },
    { headers: { ...agentHeader(), clienttype: 'cida' } }
  );
}

/**
 * 获取cloudTest迭代列表（用例执行专用）
 * 根据分支uri查询该分支下的所有迭代
 * @param versionUri - 分支uri
 * @returns Promise - 返回迭代列表
 */
export function getCloudTestIteratorsForExec(versionUri: string) {
  return agentAxiosInstance.get(
    `${apiPrefix}/testmate-exec/server/v1/cloudtest/getIterators`,
    {
      params: { versionUri, _: Date.now() },
      headers: { ...agentHeader(), clienttype: 'HTSM' }
    }
  );
}

/**
 * 根据用例编号判断用例是否在某个迭代下
 * 通过cloudTest搜索接口查询用例在指定迭代下的存在性
 * @param testCaseUri - 用例uri
 * @param versionUri - 迭代uri
 * @returns Promise - 返回搜索结果，total>0表示存在
 */
export function checkCaseInIteration(testCaseUri: string, versionUri: string) {
  return agentAxiosInstance.post(
    `${apiPrefix}/cd-tmss/v2/iteratorcase/search`,
    {
      conditions: [
        { fieldName: 'testCaseUri', fieldValue: testCaseUri, operator: '=' }
      ],
      pageNo: 1,
      pageSize: 10,
      sortField: 'creationDate|desc',
      versionUri,
      taskUri: ''
    },
    { headers: { ...agentHeader(), clienttype: 'HTSM' } }
  );
}

/**
 * 根据用例uri获取用例详情
 * 通过testcases/get接口查询用例信息，获取featureUri等字段
 * @param caseUri - 用例uri
 * @param iteratorUri - 迭代uri
 * @returns Promise - 返回用例详情
 */
export function getTestCaseInfo(caseUri: string, iteratorUri: string) {
  return agentAxiosInstance.post(
    `${apiPrefix}/cd-tmss/v2/testcases/get`,
    { uris: [caseUri] },
    {
      params: { iteratorUri, containResult: true },
      headers: { ...agentHeader(), clienttype: 'HTSM' }
    }
  );
}

/**
 * 查询cloudTest用例所在目录的层级结构
 * 获取用例在cloudTest平台中的目录树层级信息
 * @param caseUris - 用例uri数组
 * @returns Promise - 返回层级树形结构
 */
export function getCloudTestCaseHierarchy(caseUris: string[]) {
  return agentAxiosInstance.post(
    `${apiPrefix}/cd-tmss/v2/feature/structures`,
    caseUris,
    { headers: { ...agentHeader(), clienttype: 'HTSM' } }
  );
}

/**
 * cida场景批量导入用例
 * 将用例从cida平台导入到testmate-exec执行平台
 * @param params - 导入参数，包含projectId、cases层级数据等
 * @returns Promise - 返回导入结果
 */
export function batchImportCase(params: CidaBatchImportParams) {
  return agentAxiosInstance.post(
    `${apiPrefix}/testmate-exec/server/v2/case/batch-import`,
    params,
    { headers: agentHeader() }
  );
}

/**
 * cloudTest场景导入用例
 * 将用例从cloudTest平台导入到testmate-exec执行平台
 * @param params - 导入参数，包含projectId、branch/iteration信息、cases层级数据等
 * @returns Promise - 返回导入结果
 */
/**
 * cloudTest场景导迭用例到目标迭代
 * 将用例从当前分支导入到选中的迭代下
 * @param sourceVersionUri - 分支uri
 * @param destVersionUri - 目标迭代uri
 * @param sourceCaseUris - 用例uri数组
 * @returns Promise - 返回进度轮询的id
 */
export function importCaseToCloudTestIteration(
  sourceVersionUri: string,
  destVersionUri: string,
  sourceCaseUris: string[]
) {
  return agentAxiosInstance.post(
    `${apiPrefix}/cd-tmss/v3/testcase/import`,
    { sourceVersionUri, destVersionUri, sourceCaseUris },
    { headers: { ...agentHeader(), clienttype: 'HTSM' } }
  );
}

/**
 * cloudTest场景查询导入进度
 * 根据导入接口返回的进度id轮询查询导入进度
 * @param progressId - 进度轮询id
 * @returns Promise - 返回进度信息，finishedPercent为100时表示完成
 */
export function queryCloudTestImportProgress(progressId: string) {
  return agentAxiosInstance.get(
    `${apiPrefix}/cd-tmss/monitor/v2/progress/${progressId}`,
    { headers: { ...agentHeader(), clienttype: 'HTSM' } }
  );
}

/**
 * cida场景导迭用例到B版本
 * 将用例从C版本导入到选中的B版本下
 * @param sourcePaths - 用例所在目录的全路径数组
 * @param destPath - 目标B版本的全路径
 * @returns Promise - 返回进度轮询的id
 */
export function importCaseToCidaBVersion(sourcePaths: string[], destPath: string) {
  return agentAxiosInstance.post(
    `${apiPrefix}/${_tmssBaseUrl}/GT3KServer/import-service/v4/resource/import`,
    {
      including_mark: false,
      condition: {
        only_physical: false,
        physical_case_conditions: [],
        logicCase_conditions: [],
        polymorph_combination_conditions: [],
        polymorph_conditions: []
      },
      including_descendants: true,
      including_ancestors: true,
      covering: true,
      source_paths: sourcePaths,
      dest_path: destPath,
      type_names: ['TestItem', 'TestCase', 'PhysicalTestCase', 'Attachment'],
      dealing_exceptional_duplicate_number: true,
      ignore_scene_condition: false,
      dealing_exceptional_duplicate_name: true,
      import_relation_when_ignore_testcase: true,
      import_domains: [],
      update_field_configs: [
        { res_type: 'TestItem', field_names: [], is_covered_field: false },
        { res_type: 'TestCase', field_names: [], is_covered_field: false },
        { res_type: 'PhysicalTestCase', field_names: [], is_covered_field: false }
      ]
    },
    { headers: { ...agentHeader(), clienttype: 'cida' } }
  );
}

/**
 * cida场景查询导入进度
 * 根据导入接口返回的进度id轮询查询导入进度
 * @param progressId - 进度轮询id
 * @returns Promise - 返回进度信息，finishedPercent为100时表示完成
 */
export function queryCidaImportProgress(progressId: string) {
  return agentAxiosInstance.get(
    `${apiPrefix}/${_tmssBaseUrl}/GT3KServer/v0/progress/${progressId}`,
    { headers: { ...agentHeader(), clienttype: 'cida' } }
  );
}

export function importCloudTestCase(params: CloudTestImportParams) {
  return agentAxiosInstance.post(
    `${apiPrefix}/testmate-exec/server/v2/case/import`,
    params,
    { headers: agentHeader() }
  );
}

/**
 * 查询需求详情
 * 根据需求ID查询需求信息，获取integrated_system_id
 * @param requirementId - 需求ID
 * @returns Promise - 返回需求查询结果
 */
export function queryRequirementById(requirementId: string) {
  const params = [
    {
      key: 'id',
      value: [requirementId],
      operator: '||'
    },
    {
      key: 'return_fields',
      value: 'category,requirement_number,title,integrated_system_id'
    },
    {
      key: 'page_param',
      page_size: 200,
      page_no: 1
    }
  ];
  return agentAxiosInstance.post('/aidigital-test/cidaPlatform/cloud-alm/v1/requirement/query/list', params, {headers: agentHeader()});
}

/**
 * 根据用例版本和需求编号查询需求的rmUri
 * @param scope 用例版本路径
 * @param rmNumbers 需求编号列表
 * @returns 
 */
export function queryRmUriByNumber(scope: string, rmNumbers: string[]) {
  return agentAxiosInstance.post(`/aidigital-test/${_tmssBaseUrl}/GT3KServer/v1/rmRsource/number`, {
    scope,
    rmNumbers
  }, {
    headers: { ...agentHeader(), clienttype: 'cida' }
  });
}

/**
 * 创建用例和需求关联关系
 * @param params 关联参数
 * @returns 
 */
export function createCaseReqRelation(params: any) {
  return agentAxiosInstance.post(`/aidigital-test/${_tmssBaseUrl}/GT3KServer/v0/relation/caseAndParent/batch`, params, {
    headers: { ...agentHeader(), clienttype: 'cida' }
  });
}

/**
 * 创建CloudALM需求和用例关联关系
 * @param params 关联参数
 * @returns 
 */
export function createCloudAlmCaseReqRelation(params: any) {
  return agentAxiosInstance.post(`/aidigital-test/${_tmssBaseUrl}/GT3KServer/v1/relation/batch/save/multi`, params, {
    headers: { ...agentHeader(), clienttype: 'cida' }
  });
}

/**
 * 创建CloudTest用例和需求关联关系
 * @param versionUri 版本URI
 * @param params 关联参数
 * @returns 
 */
export function createCloudTestCaseReqRelation(versionUri: string, params: any) {
  return agentAxiosInstance.post(`/aidigital-test/cd-tmss/v3/relations?versionUri=${versionUri}`, params, {
    headers: { ...agentHeader(), clienttype: 'HTSM' }
  });
}
