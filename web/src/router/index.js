import Vue from 'vue';
import Router from 'vue-router';

import Pretreatment from '../components/Pretreatment.vue';
import Cleanup from '../components/Cleanup.vue';
import Upload from '../components/Upload.vue';
import Transform from '../components/Transform.vue';
import AnalyzeData from '../components/AnalyzeData.vue';
import ProblemBar from '../components/ProblemBar.vue';
import DataSource from '../components/DataSource.vue';
import Impute from '../components/Impute.vue';
import Download from '../components/Download.vue';
import NewMerge from '../components/NewMerge.vue';
import RouterView from '../components/RouterView.vue';
import analyses from '../components/vis/analyses';

Vue.use(Router);

export const routes = [
  {
    path: '/select',
    name: 'Upload Data',
    component: Upload,
  },
  {
    path: '/pretreatment/merge',
    component: NewMerge,
    props: true,
  },
  {
    path: '/pretreatment/:id',
    component: Pretreatment,
    props: true,
    meta: {
      breadcrumb(params, store) {
        const ds = store.getters.dataset(params.id);
        return {
          text: ds ? ds.name : params.id,
        };
      },
    },
    children: [
      {
        path: '',
        name: 'Pretreat Data',
        component: DataSource,
        props: true,
      },
      {
        path: 'cleanup/impute',
        name: 'Impute Table',
        component: Impute,
        props: true,
      },
      {
        path: 'cleanup',
        name: 'Clean Up Table',
        component: Cleanup,
        props: true,
        children: [
          {
            path: ':problem',
            name: 'Problem',
            component: ProblemBar,
            props: true,
          },
        ],
      },
      {
        path: 'transform',
        name: 'Transform Table',
        component: Transform,
        props: true,
      },
      {
        path: 'analyze',
        component: RouterView,
        props: true,
        meta: {
          breadcrumb() {
            return {
              text: 'Analyze Data',
            };
          },
        },
        children: [
          {
            path: '',
            name: 'Analyze Data',
            component: AnalyzeData,
            props: true,
            meta: {
              breadcrumb() {
                return {
                  hidden: true,
                };
              },
            },
          },
          ...analyses.map(({ path, shortName: name, component }) => ({
            path, name, component, props: true,
          })),
        ],
      },
      {
        path: 'download',
        name: 'Download Data',
        component: Download,
        props: true,
      },
    ],
  },
  {
    path: '/',
    name: 'Root',
    redirect: { name: 'Upload Data' },
  },
];

export default new Router({ routes });
