import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNavigation } from './src/navigation';
import { Provider } from 'react-redux';
import { store } from './src/store';

const App = () => {
  return (
    <Provider store={store}>
      <NavigationContainer>
        {createNavigation()}
      </NavigationContainer>
    </Provider>
  );
};

export default App;