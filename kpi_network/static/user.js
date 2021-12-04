// /user/:id [GET]
const userGetResponse = {
  data: {
    id: 1,
    login: 'масло1337',
    name: 'маслянко',
    status: 'lecturer',
    department: 'ПМА',
    photo: null, // || string
  },
  errors: [],
};

// /user [POST]
const userPostPayload = {
  login: 'масло1337',
  password: 'iLoveWater',
  name: 'маслянко',
  status: 'lecturer',
  department: 'ПМА',
};

const userPostResponse = {
  data: {
    id: 23,
  },
  errors: [],
};

// /user [PUT]
const userPutPayload = {
  name: 'Шияк',
  department: 'FBMI', // (or group if student)
  photo: 'base64', // || null
};

const userPutResponse = {
  data: {},
  errors: [],
};

// /user/channels?part=3&limit=2 [GET]
const userChannelsGetResponse = {
  data: {
    items: [
      {
        id: 1,
        name: 'work',
        photo: '', // || null
      },
      {
        id: 2,
        name: 'study',
        photo: '', // || null
      },
    ],

    total: 20,
  },
  errors: [],
};

const userChannelsGetFailedExample = {
  data: {
    items: [],
    total: null,
  },
  errors: ['You are not authorized'],
};
