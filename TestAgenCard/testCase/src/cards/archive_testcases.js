/**
 * 测试用例数据解析模块
 * 从JSON数据中提取测试用例
 */

export const NORMAL_RANK_MAPPING = {
  'Level 0': '6',
  'Level 1': '1',
  'Level 2': '2',
  'Level 3': '3',
  'Level 4': '4',
  'Level T': '5',
};

export const rankMapping = {
  ...NORMAL_RANK_MAPPING,
  'Level 5': '5',
  'P0': '6',
  'P1': '1',
  'P2': '2',
  'P3': '3',
  'P4': '4',
  'P5': '5',
  'PT': '5',
};

export const testTypeMapping = {
  '功能测试': '1',
  '功能测试_容错': '112',
  '性能测试': '4',
  '可靠性_可靠性测试': '22',
  '资料测试': '94',
  '可靠性_业务级可靠性测试': '95',
  '可靠性_可用性测试': '71',
  '可靠性_耐力测试': '75',
  '可靠性_容错容灾测试': '87',
  '可靠性_过载可靠性测试': '91',
  '可靠性+韧性': '28',
  '安全性_安全测试': '14',
  '安全性_韧性测试': '70',
  '安全性_隐私测试': '72',
  '安全+韧性': '27',
  '易用性_易用性测试': '15',
  '易用性_全球化测试': '23',
  '兼容性测试': '2',
  '可服务性-安装部署测试': '11',
  '可服务性_工程规划测试': '96',
  '可服务性_生产发货测试': '97',
  '可服务性_License测试': '98',
  '可服务性_验收测试': '21',
  '可服务性_扩容测试': '99',
  '可服务性_巡检测试': '100',
  '可服务性_故障处理测试': '101',
  '可服务性_补丁测试': '102',
  '可服务性_升级测试': '103',
  '可服务性_迁移测试': '104',
  'AI测试_准确性': '105',
  'AI测试_可解释性': '106',
  'AI测试_可重现': '107',
  'AI测试_公平性': '108',
  '可服务性_业务安全': '113',
  '可服务性_分权分域': '115',
  '可服务性_服务属性': '114',
  '功能性_功能交互测试': '116'
};

export const CLOUD_TEST_TYPE = {
    '0': { name: '未配置', value: '0', show: 'true', id: 'testtype_0', level: '', type: '0', order: 0,
        zh: '未配置', en: '', enable: false,
    },
    '1': { name: 'Function Test', value: '1', show: 'true', id: 'testtype_1', level: '1', type: '1', order: 1,
        zh: '功能-功能测试', en: 'Functional suitability-Function Test',  enable: true,
    },
    '2': { name: 'Compatibility Test', value: '2', show: 'true', id: 'testtype_2', level: '1', type: '1', order: 21,
        zh: '兼容性-兼容性测试', en: 'Compatibility-Compatibility Test',  enable: true,
    },
    '3': { name: 'Protocol Consistency Test', value: '3', show: 'true', id: 'testtype_3', level: '2', type: '1', order: 2,
        zh: '功能-协议一致性测试', en: 'Functional suitability-Protocol Consistency Test',  enable: true,
    },
    '4': { name: 'Performance Test', value: '4', show: 'true', id: 'testtype_4' , level: '2', type: '1', order: 3,
        zh: '性能-性能测试', en: 'Performance-Performance Test',  enable: true,
    },
    '5': { name: 'Scaling Test', value: '5', show: 'false', id: 'testtype_5', level: '', type: '2', order: 0,
        zh: 'Scaling Test', en: 'Scaling Test',  enable: false,
    },
    '6': { name: 'Pressure Test', value: '6', show: 'true', id: 'testtype_6', level: '3', type: '1', order: 9,
        zh: '可靠性-耐力测试', en: 'Reliability-Durability Test',  enable: true,
    },
    '7': { name: 'Long-run Test', value: '6', show: 'false', id: 'testtype_6', level: '', type: '3', order: 9,
        zh: '可靠性-耐力测试', en: 'Reliability-Durability Test',  enable: false,
    },
    '8': { name: 'Configuration Test', value: '8', show: 'false', id: 'testtype_8', level: '', type: '2', order: 0,
        zh: '功能-配置测试', en: 'Functional suitability-Configuration Test',  enable: false,
    },
    '9': { name: 'Recovery Test', value: '9', show: 'false', id: 'testtype_9', level: '', type: '2', order: 0,
        zh: 'Recovery Test', en: 'Recovery Test',  enable: false,
    },
    '10': { name: 'Reliability Test', value: '22', show: 'false', id: 'testtype_22', level: '', type: '3', order: 5,
        zh: '可靠性-可靠性测试', en: 'Reliability-Reliability Test', enable: false,
    },
    '11': { name: 'Installation Test', value: '11', show: 'true', id: 'testtype_11', level: '1', type: '1', order: 23,
        zh: '可服务性-可部署性测试', en: 'Serviceability-Deployment Test',  enable: true,
    },
    '12': { name: 'Traffic Control Test', value: '12', show: 'true', id: 'testtype_12', level: '2', type: '1', order: 8,
        zh: '可靠性-过载测试', en: 'Reliability-Overload Test',  enable: true,
    },
    '13': { name: 'Backup Test', value: '13', show: 'false', id: 'testtype_13', level: '', type: '2', order: 0,
        zh: 'Backup Test', en: 'Backup Test',  enable: false,
    },
    '14': { name: 'Security Test', value: '14', show: 'true', id: 'testtype_14', level: '1', type: '1', order: 12,
        zh: '安全性-安全测试', en: 'Security-Security Test',  enable: true,
    },
    '15': { name: 'Usability Test', value: '15', show: 'true', id: 'testtype_15', level: '1', type: '1', order: 18,
        zh: '易用性-易用性测试', en: 'Usability-Usability Test',  enable: true,
    },
    '16': { name: 'Maintainability Test', value: '16', show: 'true', id: 'testtype_16', level: '1', type: '1', order: 24,
        zh: '可服务性-可维护性测试', en: 'Serviceability-Maintainability Test',  enable: true,
    },
    '17': { name: 'QoS Test', value: '17', show: 'false', id: 'testtype_17', level: '', type: '2', order: 0,
        zh: 'QoS Test', en: 'QoS Test',  enable: false,
    },
    '18': { name: 'Network topology Test', value: '18', show: 'false', id: 'testtype_18', level: '', type: '2', order: 0,
        zh: 'Network topology Test', en: 'Network topology Test',  enable: false,
    },
    '19': { name: 'Interconnectivity Test', value: '19', show: 'false', id: 'testtype_19' , level: '', type: '2', order: 0,
        zh: 'Interconnectivity Test', en: 'Interconnectivity Test',  enable: false,
    },
    '20': { name: 'Stability Test', value: '20', show: 'false', id: 'testtype_20' , level: '', type: '2', order: 0,
        zh: 'Stability Test', en: 'Stability Test',  enable: false,
    },
    '21': { name: 'Serviceability Test', value: '21', show: 'true', id: 'testtype_21' , level: '1', type: '1', order: 22,
        zh: '可服务性-可服务性测试', en: 'Serviceability-Serviceability Test',  enable: true,
    },
    '22': { name: 'Reliability Test', value: '22', show: 'true', id: 'testtype_22', level: '1', type: '1', order: 5,
        zh: '可靠性-可靠性测试', en: 'Reliability-Reliability Test',  enable: true,
    },
    '23': { name: 'Globalization Test', value: '23', show: 'true', id: 'testtype_23', level: '1', type: '1', order: 20,
        zh: '易用性-全球化测试', en: 'Usability-Globalization Test',  enable: true,
    },
    '24': { name: 'Information Test', value: '23', show: 'false', id: 'testtype_23', level: '', type: '3', order: 20,
        zh: '易用性-全球化测试', en: 'Usability-Globalization Test',  enable: false,
    },
    '25': { name: 'Energy fficiency Test', value: '25', show: 'false', id: 'testtype_25', level: '', type: '2', order: 0,
        zh: 'Energy fficiency Test', en: 'Energy fficiency Test',  enable: false,
    },
    '26': { name: 'QOE Test', value: '26', show: 'false', id: 'testtype_26', level: '', type: '2', order: 0,
        zh: 'QOE Test', en: 'QOE Test',  enable: false,
    },
    '29': { name: 'Privacy Test', value: '29', show: 'true', id: 'testtype_29', level: '1', type: '1', order: 13,
        zh: '安全性-隐私测试', en: 'Security-Privacy Test',  enable: true,
    },
    '30': { name: 'Resilience Test', value: '30', show: 'true', id: 'testtype_30' , level: '1', type: '1', order: 14,
        zh: '安全性-韧性测试', en: 'Security-Resilience Test',  enable: true,
    },
    '31': { name: 'Availability Test', value: '31', show: 'true', id: 'testtype_31' , level: '1', type: '1', order: 6,
        zh: '可靠性-可用性测试', en: 'Reliability-Availability Test',  enable: true,
    },
    '32': { name: 'Security-Security Compliance Test', value: '32', show: 'true', id: 'testtype_32' , level: '3', type: '4', order: 15,
        zh: '安全性-安全遵从性测试', en: 'Security-Security Compliance Test',  enable: true,
    },
    '33': { name: 'Reliability-Fault Tolerance Test', value: '33', show: 'false', id: 'testtype_33' , level: '3', type: '4', order: 7,
        zh: '可靠性-容错容灾测试', en: 'Reliability-Fault Tolerance Test',  enable: false,
    },
    '34': { name: 'Reliability-Chaos Engineering', value: '34', show: 'false', id: 'testtype_34' , level: '', type: '2', order: 0,
        zh: '可靠性-混沌测试', en: 'Reliability-Chaos Engineering',  enable: false,
    },
    '35': { name: 'Security-Anti-Attack Test', value: '35', show: 'true', id: 'testtype_35' , level: '3', type: '4', order: 16,
        zh: '安全性-抗攻击性测试', en: 'Security-Anti-Attack Test',  enable: true,
    },
    '36': { name: 'Testability-Testability', value: '36', show: 'false', id: 'testtype_36' , level: '', type: '2', order: 0,
        zh: '可测试性-可测试性', en: 'Testability-Testability',  enable: false,
    },
    '37': { name: 'AI-Accuracy Test', value: '37', show: 'false', id: 'testtype_37' , level: '2', type: '4', order: 26,
        zh: 'AI测试-准确性测试', en: 'AI-Accuracy Test',  enable: false,
    },
    '38': { name: 'AI-Generalization Ability Test', value: '38', show: 'false', id: 'testtype_38' , level: '', type: '2', order: 0,
        zh: 'AI测试-泛化性测试', en: 'AI-Generalization Ability Test',  enable: false,
    },
    '39': { name: 'AI-Explainability Test', value: '39', show: 'false', id: 'testtype_39' , level: '2', type: '4', order: 27,
        zh: 'AI测试-可解释性测试', en: 'AI-Explainability Test',  enable: false,
    },
    '40': { name: 'AI-Reproducibility Test', value: '40', show: 'false', id: 'testtype_40' , level: '2', type: '4', order: 28,
        zh: 'AI测试-可重现测试', en: 'AI-Reproducibility Test',  enable: false,
    },
    '41': { name: 'AI-Non-Discrimination Test', value: '41', show: 'false', id: 'testtype_41' , level: '', type: '2', order: 0,
        zh: 'AI测试-非歧视测试', en: 'AI-Non-Discrimination Test',  enable: false,
    },
    '42': { name: 'AI-Robustness Test', value: '42', show: 'false', id: 'testtype_42' , level: '', type: '2', order: 0,
        zh: 'AI测试-鲁棒性测试', en: 'AI-Robustness Test',  enable: false,
    },
    '43': { name: 'Energy Consumption Test', value: '43', show: 'true', id: 'testtype_43' , level: '3', type: '4', order: 4,
        zh: '性能-能耗测试', en: 'Performance-Energy Consumption Test',  enable: true,
    },
    '44': { name: 'Stress Test', value: '44', show: 'false', id: 'testtype_44' , level: '3', type: '4', order: 10,
        zh: '可靠性-压力测试', en: 'Reliability-Stress Test',  enable: false,
    },
    '45': { name: 'Recovery Test', value: '45', show: 'false', id: 'testtype_45' , level: '3', type: '4', order: 11,
        zh: '可靠性-恢复测试', en: 'Reliability-Recovery Test',  enable: false,
    },
    '46': { name: 'Whitebox Security Test', value: '46', show: 'false', id: 'testtype_46' , level: '3', type: '4', order: 17,
        zh: '安全性-白盒安全测试', en: 'Security-Whitebox Security Test',  enable: false,
    },
    '47': { name: 'User Experience Test', value: '47', show: 'true', id: 'testtype_47' , level: '3', type: '4', order: 19,
        zh: '易用性-体验测试', en: 'Usability-User Experience Test',  enable: true,
    },
    '48': { name: 'AI Test', value: '48', show: 'true', id: 'testtype_48' , level: '2', type: '4', order: 25,
        zh: 'AI测试', en: 'AI-AI Test',  enable: true,
    },
    '49': { name: 'AI-Fairness Test', value: '49', show: 'false', id: 'testtype_49' , level: '2', type: '4', order: 29,
        zh: 'AI测试-公平性测试', en: 'AI-Fairness Test',  enable: false,
    },
};

/**
 * 从JSON数据中提取测试用例列表
 * @param {Object|Array} data - 输入的JSON数据
 * @param {string[]} [filterNames] - 用例名称过滤列表（可选）
 * @returns {Array} 提取的测试用例列表
 */
export function extractTestcases(data, filterNames = []) {
  let testcases = [];
  
  if (!data) {
    return testcases;
  }

  if (Array.isArray(data)) {
    testcases = data;
  } else if (data.test_point_list) {
    data.test_point_list.forEach(tp => {
      if (tp.test_case_list) {
        tp.test_case_list.forEach(tc => {
          if (filterNames && filterNames.length > 0) {
            if (filterNames.includes(tc.name)) {
              testcases.push(tc);
            }
          } else {
            testcases.push(tc);
          }
        });
      }
    });
  } else if (data.testcases) {
    testcases = data.testcases;
  }

  return testcases;
}

/**
 * 将测试用例转换为CIDA API请求格式
 * @param {Object} testcase - 测试用例数据
 * @param {string} username - 用户名
 * @returns {Object} CIDA API请求数据
 */
export function transformToCidaRequest(testcase, username = '', session) {
  const priority = testcase.priority || 'Level 2';
  const rank = rankMapping[priority] || '2';
  const testType = testTypeMapping[testcase.type] || '1';

  return {
    type: 'TestCase',
    rank: rank,
    TestType: testType,
    Preparation: testcase.pre || '',
    TestStep: testcase.test_step || '',
    ExpectOutput: testcase.expect_output || '',
    number: testcase.number || '',
    name: testcase.name || '',
    atpFlag: '3',
    testMindId: String(session?.id ? session.id: '1'),
    testMindUrl: window.parent.location.href,
  };
}

/**
 * 批量转换测试用例为CIDA请求格式
 * @param {Array} testcases - 测试用例列表
 * @param {string} username - 用户名
 * @returns {Array} CIDA请求数据列表
 */
export function batchTransformTestcases(testcases, username = '') {
  return testcases.map(tc => transformToCidaRequest(tc, username));
}
