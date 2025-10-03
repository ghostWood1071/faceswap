angular.module('imageApp', [])
      .controller('MainCtrl', ['$scope', '$http', function($scope, $http) {
        $scope.sourceImages = [];
        $scope.targetImages = [];
        $scope.selectedSource = null;
        $scope.selectedTargets = [];
        $scope.paramMin = 0;
        $scope.paramMax = 300;
        $scope.menuOpen = false;
        $scope.selectionType = '';
        $scope.pages = [
          { name: 'Trang chính' },
          { name: 'Ảnh đã xử lý' },
          { name: 'Cấu hình' }
        ];

        $scope.goToPage = function(page) {
          alert('Chuyển đến: ' + page.name);
        };

        function isFileUrl(url) {
          return url.startsWith("https://")
        }

        function get_src(paths){
            results = []
            for (path of paths){
                check = isFileUrl(path)
                type = 'img'
                if (check == false)
                    type = 'folder'
                results.push({"url": path, "type": type})
            }
            return results
        }

        $scope.loadSource = (path)=> {
          $http.get(
            '/api/source-list',
            {
                "params": {
                    "path": path
                }
            }
          ).then(res => {
            paths = res.data
            results = get_src(paths)
            $scope.sourceImages = results
          });

        }

        $scope.loadTarget = (path)=> {
          $http.get(
            '/api/target-list',
            {
                "params": {
                    "path": path
                }
            }
          ).then(res => {
            paths = res.data
            results = get_src(paths)
            $scope.targetImages = results
          });

        }

        $scope.selectSource = function(img) {
          console.log(img)
          $scope.selectedSource = img;
        };

        $scope.toggleTarget = function(img) {
          const idx = $scope.selectedTargets.indexOf(img);
          if (idx > -1) {
            $scope.selectedTargets.splice(idx, 1);
          } else {
            $scope.selectedTargets.push(img);
          }
        };

        $scope.callProcessApi = function() {
          if (!$scope.selectedSource || $scope.selectedTargets.length === 0) {
            alert("Vui lòng chọn ảnh nguồn và ít nhất 1 ảnh mục tiêu hoặc thư mục.");
            return;
          }
          const data = {
            source: $scope.selectedSource.url,
            targets: $scope.selectedTargets,
            paramRange: [$scope.paramMin, $scope.paramMax]
          };
          $http.post('/api/process', data).then(
            () => alert("✅ Thành công!"),
            () => alert("❌ Thất bại!")
          );
        };

        $scope.downloadResult = function() {
          $http.post('/api/download', {}).then(
            () => alert("✅ Tải thành công!"),
            () => alert("❌ Tải thất bại!")
          );
        };

        $scope.loadSource(null)
        $scope.loadTarget(null)
      }]);